
import dask.dataframe as dd
import dask.bag as db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time
import pandas as pd
from pipeline import Component
from devgpt_pipeline.models.model import Issue, PullRequest, Commit, Discussion, Sharing, Conversation, Language, HackerNews
# from dask_config.get_dask import get_dask_client
# A test attempt to extract name and email from text
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup
import ssl
from nltk.stem.snowball import SnowballStemmer
import nltk

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('stopwords')
nltk.download('punkt')
from nltk.tokenize import word_tokenize

from deep_translator import GoogleTranslator  

import ssl
ssl._create_default_https_context = ssl._create_unverified_context



def strip_numeric(text):
    return re.sub(r'\d+', '', text)

def strip_punctuation(text):
    return re.sub(r'[^\w\s]', '', text)

def strip_multiple_whitespaces(text):
    return re.sub(r'\s+', ' ', text).strip()

def remove_newline(text):
    return text.replace('\n', '')

def transform_to_lower(text):
    return text.lower()

def remove_stopwords(text):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return ' '.join(filtered_words)

def remove_single_char(text):
    words = word_tokenize(text)
    filtered_words = [word for word in words if len(word) > 1]
    return ' '.join(filtered_words)

def stem_text(text):
    stemmer = SnowballStemmer("english")
    words = word_tokenize(text)
    stemmed_words = [stemmer.stem(word) for word in words]
    return ' '.join(stemmed_words)

def clean_text(text):
    if text is None:
        return ""
    text = strip_numeric(text)
    text = strip_punctuation(text)
    text = remove_newline(text)
    text = strip_multiple_whitespaces(text)
    text = transform_to_lower(text)
    text = remove_single_char(text)
    text = stem_text(text)
    return text


class LanguageTranslatorComponent(Component):
    def __init__(self):
        super().__init__('Language Detection')
        self.database_url = "sqlite:///devgpt.sqlite"
        self.session = self.get_session().__next__()
        self.columns_to_detect = {
            'issue': ['title', 'body'],
            # 'pull_request': ['title', 'body'],
            # 'commit': ['message'],
            # 'discussion': ['title', 'body'],
            # 'sharing': ['title'],
            # 'conversation': ['Prompt', 'Answer'],
            # 'hackernews': ['title']

        }
        self.table_obj = {
            'issue': Issue,
            # 'pull_request': PullRequest,
            # 'commit': Commit,
            # 'discussion': Discussion,
            # 'sharing': Sharing,
            # 'conversation': Conversation,
            # 'hackernews': HackerNews
        }
    
    def get_session(self):
        # use yield to create a session 
        engine = create_engine(self.database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
    
    @staticmethod
    def __clean_text(text):
        return clean_text(text)
    # @staticmethod
    # def chunk_text(word_list):
    #     '''Break the word_list into chunks of 4500 characters'''
    #     chunks = []
    #     chunk = ''


    @staticmethod
    def translate_language(text):

        '''Translate the text to English'''
        if text is None:
            return []
        
        if len(text) > 5000:
            # Break the text into chunks of 4500 characters and translate each chunk
            chunks = [text[i:i+4500] for i in range(0, len(text), 4500)]
            translated_chunks = []


            for chunk in chunks:
                time.sleep(1)
                try:
                    translated_chunks.append(GoogleTranslator(source='auto', target='en').translate(chunk))
                except Exception as e:
                    print(f"Failed to translate chunk:")
                    translated_chunks.append(chunk)

            translated_text = ''.join(translated_chunks)
            return translated_text

        try: 
            translated_text = GoogleTranslator(source='auto', target='en').translate(text)
        except Exception as e:
            time.sleep(4)
            translated_text = text

        time.sleep(1)
        return translated_text

    def __get_data_from_table(self, table):
        columns = self.columns_to_detect[table]
        # language_id is not en
        # language does not have "translated"
        query = f'SELECT id, snapshot_id, {", ".join(columns)} FROM "{table}" WHERE  language is not "translated" and language_id is not "en";'
        try:
            df = pd.read_sql_query(query, self.database_url)
            print(f"Successfully read data from {table}")
        except Exception as e:
            raise Exception(f"Failed to read data from {table}: {e}")
        return df


    def process(self):
        session = self.get_session().__next__()

        print("Language Translation component started processing")

        for table, columns in self.columns_to_detect.items():
            # wait for 10 seconds

            mdf = self.__get_data_from_table(table)
            # order by id
            mdf = mdf.sort_values(by=['id'])
            print(f"Successfully read {len(mdf)} rows from {table}")
            # translate 200 rows at a time
            chunks = [mdf[i:i+200] for i in range(0, len(mdf), 200)]
            print(f"Number of chunks: {len(chunks)}")
            count = 0
            for df in chunks:
                print(f"Processing {len(df)} rows from {table}")
                print(f"Processing chunk {count}")
                table_ddf = dd.from_pandas(df, npartitions=4)
                table_ddf = table_ddf.fillna('')
                for column in columns:
                    table_ddf[f'{column}'] = table_ddf[column].apply(LanguageTranslatorComponent.__clean_text, meta=(f'{column}', 'str'))
                    table_ddf[f'{column}'] = table_ddf[column].apply(LanguageTranslatorComponent.translate_language, meta=(f'{column}', 'str'))
                result_df = table_ddf.compute()
                print(f"Successfully translated {len(result_df)} rows from {table}")
                print(result_df.head())

                # Update the database using SQLAlchemy
                for _, row in result_df.iterrows():
                    record = session.query(self.table_obj[table]).filter_by(id=row['id'], snapshot_id=row['snapshot_id']).first()
                    if record:
                        record.language = "translated"
                        # if we are translating more than one column
                        for column in columns:
                            setattr(record, column, row[column])
                        session.add(record)
                    else:
                        # if the rcord does not exist, raise an exception
                        raise Exception(f"Record with id {row['id']} and snapshot {row['snapshot']} does not exist in table {table}")
                session.commit()
                time.sleep(10)
                count += 1

        session.close()
        print("Language detection component finished processing")
        
