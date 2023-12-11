from preprocessing.text_cleaning.clean_text import PreprocessEnglishText
from sqlalchemy import create_engine
from devgpt_pipeline.models.model import Conversation, Issue, PullRequest, Commit, Sharing
from sqlalchemy.orm import sessionmaker
import sqlalchemy
import pandas as pd
import os
import dask
import dask.dataframe as dd
from sentence_transformers import SentenceTransformer
from dask import delayed
import faiss
import numpy as np
from dask.distributed import Client, LocalCluster, wait


class SemanticSearch:
    def __init__(self):
        self.database_url = 'sqlite:///devgpt.sqlite'
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.ddf = None
        self.embeddings = None
        self.tables = [
        # (Conversation, ['Prompt', 'Answer', 'language_id']),
        (Issue, ['body', 'title', 'language_id']),
        # (PullRequest, ['body', 'title', 'language_id']),
        # (Commit, ['message', 'language_id'])
        ]
        self.lang = 'en'
        self.auto_detect_text = PreprocessEnglishText.auto_detect_text
        self.clean_text = PreprocessEnglishText().preprocess_text


    def get_df_dask (self, table):
        session = self.Session()
        table,columns = table[0], table[1]
        # get all rows from the table where language_id is en
        query = self.session.query(table).filter(table.language_id == self.lang)
        # create a dask dataframe from the query
        df = pd.read_sql(query.statement, query.session.bind, index_col=['id', 'snapshot_id'])
        # combine the id and snapshot_id into one column
        df.index = df.index.map(lambda x: f'{x[0]}_{x[1]}')
        # id column is id and snapshot_id combined
        df['id'] = df.index
        ddf = dd.from_pandas(df, npartitions=10)
        # get only the columns we want, drop language_id which the last column
        columns = columns[:-1]
        columns.append('id')
        print(columns)
        ddf = ddf[columns]
        # drop duplicates
        ddf = ddf.drop_duplicates()
        return ddf
    
    def clean_ddf(self, df, text_columns=None):
        # clean the text data
        for column in text_columns:
            df[column] = df[column].map(self.clean_text, meta=('x', 'object'))
        return df
    @staticmethod
    def get_embeddings( column):
        model = SentenceTransformer('msmarco-distilbert-base-v3')
        embeddings = model.encode(column)
        return embeddings

    def merge_columns(self, df, text_columns):
        df['text'] = df[text_columns].apply(lambda x: ' '.join(x), axis=1, meta=('x', 'object'))
        text_columns.remove('id')
        df = df.drop(columns=text_columns)
        return df

    def index_it(self, embeddings):
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        return index

    @staticmethod
    @delayed
    def search(query, table, df):
        index = faiss.read_index(f'indexes/{table}.index')
        query_embedding = SemanticSearch.get_embeddings(query)
        top_k = index.search(query_embedding.reshape(1, -1), 1000)
        _, indices = top_k

        id_list = df.iloc[indices[0]]['id'].tolist()
        # remove the last character from the id
        id_list = list(set([id[:-2] for id in id_list]))

        return id_list

    def run_search(self, table, merged_df):
        if os.path.isfile(f'indexes/{table[0].__table__.name}.index'):
            tablename = table[0].__table__.name
            keywordfile = 'keywords.csv'
            keywords = pd.read_csv(keywordfile)
            
            search_list = keywords['keyword'].tolist()
            futures = []

            for query in search_list:
                future = self.search(query, tablename, merged_df)
                futures.append(future)

            # Wait for all futures to complete
            wait(futures)

            # Retrieve results
            results = dask.compute(*futures)

            # Save the results in a DataFrame
            df = pd.DataFrame(columns=['keyword', 'id_list'])
            for i, result in enumerate(results):
                df.loc[i] = [search_list[i], result]

            # Save the DataFrame to a CSV file
            df.to_csv(f'subset/sc/{tablename}.csv', index=False)
            print(df)
    
    def run(self):
        # Create Dask cluster and client
        session = self.Session()
        cluster = LocalCluster()
        client = Client(cluster)
        dashboard_link = client.dashboard_link
        print(dashboard_link)

        for table in self.tables:
            ddf = self.get_df_dask(table)

            text_columns = PreprocessEnglishText().auto_detect_text(ddf)
            clean_ddf = self.clean_ddf(ddf, text_columns)
            clean_ddf = clean_ddf.compute()

            # last character of the id is the snapshot_id
            clean_ddf['snapshot_id'] = clean_ddf['id'].map(lambda x: x[-1])
            clean_ddf['id'] = clean_ddf['id'].map(lambda x: x[:-2])
            clean_ddf = clean_ddf.set_index(['id', 'snapshot_id'])

            # Assuming 'YourTable' is the SQLAlchemy model associated with 'table[0]'
            data = session.query(table[0]).filter(table[0].language_id == self.lang).all()

            # Update the database with the cleaned text
            for row in clean_ddf.itertuples():
                matching_row = next((d for d in data if d.id == row.Index[0] and d.snapshot_id == row.Index[1]), None)
                if matching_row:
                    for column in text_columns:
                        setattr(matching_row, column, row.__getattribute__(column))

            # Commit the changes to the database outside the inner loop
            session.commit()

        #     merged_df = self.merge_columns(clean_ddf, text_columns)
        #     if not os.path.isfile(f'indexes/{table[0].__table__.name}.index'):
        #         embeddings = self.get_embeddings(merged_df['text'])
        #         index = self.index_it(embeddings)
        #         faiss.write_index(index, f'indexes/{table[0].__table__.name}.index')
        #         print('index created')
        #     # Scatter the dataframe to the workers
        #     merged_df_future = client.scatter(merged_df.compute(), broadcast=True)

        #     # Run the search for each table
        #     self.run_search(table, merged_df_future)

        # # Close the Dask client and cluster
        # client.close()
        # cluster.close()

# Assuming you have a class method get_embeddings in YourClass