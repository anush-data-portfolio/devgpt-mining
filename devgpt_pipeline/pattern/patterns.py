from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import time
from pipeline import Component
from devgpt_pipeline.models.model import Issue, PullRequest, Commit, Discussion, Sharing, Conversation, Language, HackerNews
import pandas as pd

import re
import os

from dask.distributed import Client, LocalCluster
import dask.dataframe as dd


class KeywordPatternsComponent(Component):
    def __init__(self,  data_folder="filtered_data"):
        super().__init__('Keyword Filter')
        self.database_url = "sqlite:///devgpt.sqlite"
        self.session = self.get_session().__next__()
        self.columns_to_clean = {
            Conversation: ['Prompt', 'Answer', 'id', 'snapshot_id','ListOfCode'],
            # Issue: ['body', 'title', 'id', 'snapshot_id'],
            # PullRequest: ['body', 'title', 'id', 'snapshot_id'],
            # Commit: ['message', 'id', 'snapshot_id'],
            # Discussion: ['body', 'title', 'id', 'snapshot_id'],
            # Sharing: [ 'title', 'id', 'snapshot_id'],
            # HackerNews: ['title', 'id', 'snapshot_id']
        }
        self.keyword_folder = "keywords/"
        self.keywords = {
            'QA' : "QA.csv",
            # 'refactor': "refactor.csv",
            # 'intent' : "intent.csv",
            # 'SAR': "SAR.csv",

        }
        self.output_folder = output_folder
        self.data_folder = data_folder

    def regex_match(self, string_vec, keyword):
        ''' Match a keyword with * with a string vector using regular expressions
        replac* -> replace, replacing, replacement, etc.
        '''
        if not string_vec or not keyword:
            return False
        keyword = keyword.replace("*", ".*")
        keyword = keyword.lower()
        if isinstance(string_vec, list):
            string_vec = " ".join(string_vec)
        if re.search(keyword, string_vec):
                return True
        return False

    def check_phrase_match(self, string_vec, keyword):
        if not string_vec or not keyword:
            return False

        for i in range(len(string_vec) - len(keyword) + 1):
            window_elements = string_vec
            if all(word in window_elements for word in keyword):
                return True
        return False

    def check_for_match(self, string_vec, keyword):
        
        if '*' in keyword:
            return self.regex_match(string_vec, keyword)
        if string_vec is None:
            return False
        if len(keyword.split(" ")) > 1:
            return self.check_phrase_match(string_vec, keyword.split(" "))
        if keyword.lower() in string_vec:
            return True
        return False

    def row_check(self, row, keywords, table_name):

        row = row.to_dict()
        matches = []
        except_cols = ['id', 'snapshot_id']
        for col in row.keys():
            if col not in except_cols:
                string_vec = row[col]
                if string_vec is None or len(string_vec) == 0:
                    continue
                for keyword in keywords:
                    if self.check_for_match(string_vec, keyword):
                        matches.append({'id': row['id'], 'snapshot_id': row['snapshot_id'], 'keyword': keyword, 'col': col,
                                            'table': table_name}) 
        return matches

    def get_keywords(self, keyword_type):
        df = pd.read_csv(self.keyword_folder + self.keywords[keyword_type])
        keywords = df['keyword'].tolist()
        return [k.lower() for k in keywords]
    
    def __create_dask_client(self):
        cluster = LocalCluster()
        client = Client(cluster)
        print(f"Dashboard link: {client.dashboard_link}")
        return client
    
    def check_if_folder_exists(self, folder):
        if os.path.isdir(folder):
            return True
        try:
            os.mkdir(folder)
            return True
        except Exception as e:
            print(f"Failed to create folder {folder}: {e}")
            return False
        return True
    
    def get_session(self):
        engine = create_engine(self.database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
    



    def process(self, data=None):
        print("Starting Keyword Filter")
        for table, columns in self.columns_to_clean.items():
            data = pd.read_csv(f"{self.data_folder}/{table.__tablename__}.csv")
            keywords = self.keywords.keys()
            for keyword_type in keywords:
                keywords = self.get_keywords(keyword_type)
                print(f"Checking for {keyword_type} keywords in {table.__tablename__}")
                chunks = [data[i:i+5000] for i in range(0, len(data), 5000)]
                counter = 0
                merge_matches_df = pd.DataFrame()
                for df in chunks:
                    print(f"\nProcessing Chunk: {counter}, {df.shape}")
                    # # Keyword matching with Dask
                    ddf = dd.from_pandas(df, npartitions=round(len(df)/50 ))
                    print(keywords )
                    matches = ddf.map_partitions(lambda part: part.apply(self.row_check, args=(keywords, table.__tablename__), axis=1))
                    matches = matches.compute(scheduler='threads')

                    matches = [item for sublist in matches for item in sublist]
                    matches = pd.DataFrame(matches)

                    if not matches.empty:
                        merge_matches_df = pd.concat([merge_matches_df, matches], ignore_index=True)
                    counter+=1 
                self.check_if_folder_exists(self.output_folder)
                merge_matches_df.to_csv(f'{self.output_folder}/{keyword_type}/{table.__tablename__}.csv', index=False)

        print("Finished Keyword Filter")


                
        
