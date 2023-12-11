
import dask.dataframe as dd
import dask.bag as db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pandas as pd
from pipeline import Component
from devgpt_pipeline.models.model import (
    Issue, PullRequest, Commit, Discussion, Sharing, Conversation, Language, HackerNews)

from nltk.tokenize import word_tokenize
import fasttext
fasttext.FastText.eprint = lambda x: None

import nltk
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


class LanguageDetectionComponent(Component):
    def __init__(self):
        super().__init__('Language Detection')
        self.database_url = "sqlite:///devgpt.sqlite"
        self.session = self.get_session().__next__()
        self.columns_to_detect = {
            'issue': ['title', 'body'],
            'pull_request': ['title', 'body'],
            'commit': ['message'],
            'discussion': ['title', 'body'],
            'sharing': ['title'],
            'conversation': ['Prompt', 'Answer'],
            'hackernews': ['title']

        }
        self.table_obj = {
            'issue': Issue,
            'pull_request': PullRequest,
            'commit': Commit,
            'discussion': Discussion,
            'sharing': Sharing,
            'conversation': Conversation,
            'hackernews': HackerNews
        }
        nltk.download('stopwords')
        nltk.download('punkt')
        self.lang_code_json = "devgpt_pipeline/lang_detect/langcode.json"
        self.lang_code_dict = pd.read_json(self.lang_code_json, typ='series').to_dict()
        self.__update_languages()    


    def get_session(self):
        engine = create_engine(self.database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session

    @staticmethod
    def clean_text( text):
        '''Clean the multi-lingual text by removing stop words and punctuation
        '''
        tokens = word_tokenize(text)
        tokens = [word.lower() for word in tokens if word.isalpha()]
        tokens = [word.replace('\\n', '') for word in tokens]
        return ' '.join(tokens)
    @staticmethod
    def detect_language( text):
        '''Detect the language of the text using fasttext'''
        text = LanguageDetectionComponent.clean_text(text)
        language_classifier = fasttext.load_model('model/lid.176.bin')
        language = language_classifier.predict(text)
        language = language[0][0].split('__')[-1], language[1][0]
        return language
    
    def __update_languages(self):
        for language_code in self.lang_code_dict.keys():
            self.__update_language(language_code)

    def __update_language(self, language_code):
        lang_name = self.lang_code_dict[language_code]
        if not self.session.query(Language).filter_by(code=language_code).first():
            self.session.add(Language(code=language_code, name=lang_name))
            self.session.commit()
    

    def __get_data_from_table(self, table):
        columns = self.columns_to_detect[table]
        query = f'SELECT id, snapshot_id, {", ".join(columns)} FROM "{table}";'
        try:
            df = pd.read_sql_query(query, self.database_url)
            print(f"Successfully read data from {table}")
        except Exception as e:
            raise Exception(f"Failed to read data from {table}: {e}")
        return df


    def process(self, data=None):
        session = self.get_session().__next__()
        results = {}
        print("Language detection component started processing")

        for table, columns in self.columns_to_detect.items():
            df = self.__get_data_from_table(table)
            df_chunks = [df[i:i+1000] for i in range(0, len(df), 1000)]
            for cdf in df_chunks:
                print(f"Processing {len(cdf)} rows from {table}")
                table_ddf = dd.from_pandas(cdf, npartitions=10)
                table_ddf = table_ddf.fillna('')
                for column in columns:
                    table_ddf[f'{column}_language'] = table_ddf[column].apply(self.detect_language, meta=(f'{column}_language', 'str'))
                result_df = table_ddf.compute()
                print(f"Finished detecting language for {table}")
                for _, row in result_df.iterrows():
                    record = session.query(self.table_obj[table]).filter_by(id=row['id'], snapshot_id=row['snapshot_id']).first()
                    if record:
                        lang_code_prob = []
                        for column in columns:
                            lang_code_prob.append(row[f'{column}_language'])
                        record.language_id = max(lang_code_prob, key=lambda x: x[1])[0]
                        session.add(record)
                    else:
                        raise Exception(f"Record with id {row['id']} and snapshot {row['snapshot']} does not exist in table {table}")
                session.commit()
                results[table] = len(result_df)
                print(f"Successfully updated {len(result_df)} rows in {table}")

        session.close()
        return f"Language detection Component finished processing {len(results)} tables"
