from pipeline import Component
import dask.dataframe as dd
import pandas as pd
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from spacy.lang.en import English
import string
import re

class PreprocessEnglishText:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.stop_words = STOP_WORDS
        self.punctuations = string.punctuation
        self.df = None
        self.tokens = ['CHATGPT_SHARE_LINK']

    def remove_stopwords(self, text):
        return ' '.join([word for word in text.split() if word.lower() not in self.stop_words])

    def remove_punctuation(self, text):
        # Define a translation table to remove punctuation
        translation_table = str.maketrans("", "", string.punctuation)

        # Split the text into tokens
        tokens = text.split()

        # Remove punctuation only for tokens not in self.tokens
        cleaned_tokens = [token.translate(translation_table) if token not in self.tokens else token for token in tokens]

        # Join the cleaned tokens back into a string
        cleaned_text = ' '.join(cleaned_tokens)

        return cleaned_text

    def lemmatize(self, text):
        doc = self.nlp(text)
        return ' '.join([token.lemma_ for token in doc])


    def replace_chatgpt_share_link(self, input_text):
        pattern = r'https://chat\.openai\.com/share/[a-zA-Z0-9-]+'
        result_text = re.sub(pattern, 'CHATGPT_SHARE_LINK', input_text)
        return result_text

    def preprocess_text(self, text):
        if text is None:
            return ""
        text = text.lower()
        text = self.replace_chatgpt_share_link(text)
        text = self.remove_stopwords(text)
        text = self.remove_punctuation(text)
        text = self.lemmatize(text)
        return text


    
    @staticmethod
    def auto_detect_text( df):
        # auto detect all text columns
        text_columns = []
        for column in df.columns:
            if df[column].dtype == 'object':
                text_columns.append(column)
        return text_columns
    
    # def run(self, df, column_names=None):
    #     if column_names is None:
    #         column_names = self.auto_detect_text(df)
    #     self.df = df
    #     for column_name in column_names:
    #         self.preprocess_column(column_name)
    #     return self.df

