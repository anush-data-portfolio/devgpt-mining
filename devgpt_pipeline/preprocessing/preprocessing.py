from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import string

import time
from pipeline import Component
from devgpt_pipeline.models.model import (
    Issue, PullRequest, Commit, Discussion, Sharing, Conversation, Language, HackerNews)
import pandas as pd

import re
import os

from dask.distributed import Client, LocalCluster
import dask.dataframe as dd


import ssl
ssl._create_default_https_context = ssl._create_unverified_context

spacy_nlp = spacy.load('en_core_web_sm')




class PreProcessorComponent(Component):
    def __init__(self,  output_folder="tokenised_data"):
        super().__init__('PreProcessor')
        self.database_url = "sqlite:///devgpt.sqlite"
        self.session = self.get_session().__next__()
        self.columns_to_clean = {
            Conversation: ['Prompt', 'Answer', 'id', 'snapshot_id','ListOfCode'],
            Issue: ['body', 'title', 'id', 'snapshot_id'],
            PullRequest: ['body', 'title', 'id', 'snapshot_id'],
            Commit: ['message', 'id', 'snapshot_id'],
            Discussion: ['body', 'title', 'id', 'snapshot_id'],
            Sharing: [ 'title', 'id', 'snapshot_id'],
            HackerNews: ['title', 'id', 'snapshot_id']
        }
        self.output_folder = output_folder
    
    def merge_all_df(self, folder_path, output_file):
        csv_files = [file for file in os.listdir(folder_path) if file.endswith(".csv")]

        merged_df = pd.DataFrame()

        for csv_file in csv_files:
            file_path = os.path.join(folder_path, csv_file)
            df_chunk = pd.read_csv(file_path)
            merged_df = pd.concat([merged_df, df_chunk], ignore_index=True)

        merged_df.to_csv(output_file, index=False)
        for csv_file in csv_files:
            file_path = os.path.join(folder_path, csv_file)
            os.remove(file_path)
        self.delete_temp_folder(folder_path)
        return output_file


    def __generate_sql_query(self, table, columns):
        query = self.session.query(*[getattr(table, c) for c in columns])
        return query
    
    def __create_dask_client(self):
        cluster = LocalCluster()
        client = Client(cluster)
        print(f"Dashboard link: {client.dashboard_link}")
        return client

    @staticmethod   
    def __spacy_tokenizer(sentence):
        punctuations = string.punctuation
        stop_words = STOP_WORDS
        if sentence is None:
            return []
        sentence = sentence.lower()


        sentence = re.sub('\'','',sentence)

        sentence = re.sub('\w*\d\w*','',sentence)

        sentence = re.sub(' +',' ',sentence)

        sentence = re.sub(r'\n: \'\'.*','',sentence)
        sentence = re.sub(r'\n!.*','',sentence)
        sentence = re.sub(r'^:\'\'.*','',sentence)
        
        sentence = re.sub(r'\n',' ',sentence)
        
        sentence = re.sub(r'[^\w\s]',' ',sentence)
        
        tokens = spacy_nlp(sentence)
        
        tokens = [word.lemma_.lower().strip() if word.lemma_ != "-PRON-" else word.lower_ for word in tokens]
        
        tokens = [word for word in tokens if word not in stop_words and word not in punctuations and len(word) > 2]
        
        return tokens
    
    def get_temp_folder(self):
        import tempfile
        return tempfile.mkdtemp()
    
    def delete_temp_folder(self, folder):
        import shutil
        shutil.rmtree(folder)
    
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
        print("Starting PreProcessor")
        for table, columns in self.columns_to_clean.items():
            query = self.__generate_sql_query(table, columns)
            chunksize = 5000
            chunk = 0
            for df in pd.read_sql(query.statement, query.session.bind, chunksize=chunksize):
                print(f"Processing chunk {chunk} of {table.__tablename__}")
                cols_to_tokenize = df.columns.difference(['id', 'snapshot_id'])
                df_len = len(df)
                num_partitions = round(df_len / 50)

                ddf = dd.from_pandas(df, npartitions=num_partitions)
                ddf = ddf.assign(**{col: ddf[col].apply(PreProcessorComponent.__spacy_tokenizer, meta=(col, 'object')) for col in cols_to_tokenize}).compute()
                folder = self.get_temp_folder()
                ddf.to_csv(f'{folder}/chunk_{chunk}_{table.__tablename__}.csv', index=False)
                print(f"Writting to CSV: chunk_{chunk}_{table.__tablename__}.csv")
                chunk+=1
            try:
                self.check_if_folder_exists(self.output_folder)
                self.merge_all_df(folder, f'{self.output_folder}/{table.__tablename__}.csv')
            except Exception as e:
                print(f"Failed to merge CSVs: {e}")
                raise e 
        print("Finished PreProcessor")

        



        
