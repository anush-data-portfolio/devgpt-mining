import dask.dataframe as dd
import dask.bag as db
import spacy
from spacy.language import Language
import sqlite3

# Function to detect language using Spacy
def detect_language(text):
    doc = nlp(text)
    return doc._.language['language']

# Initialize Spacy's language detection model
nlp = spacy.load("en_core_web_sm")

# Connect to the SQLite database
conn = sqlite3.connect('devgpt.sqlite')

# Create a Dask dataframe from the 'issue' table
issues_df = dd.read_sql_table('issue', 'sqlite:///devgpt.sqlite')

# Create a Dask dataframe from the 'conversation' table
conversation_df = dd.read_sql_table('conversation', 'sqlite:///devgpt.sqlite')

# Apply language detection to issue titles and bodies
issues_df['title_language'] = issues_df['title'].apply(detect_language, meta=('title_language', 'str'))
issues_df['body_language'] = issues_df['body'].apply(detect_language, meta=('body_language', 'str'))

# Apply language detection to chatGPT prompts and answers
conversation_df['Prompt_language'] = conversation_df['Prompt'].apply(detect_language, meta=('Prompt_language', 'str'))
conversation_df['Answer_language'] = conversation_df['Answer'].apply(detect_language, meta=('Answer_language', 'str'))

# Compute the Dask dataframes to get the results
issues_result = issues_df.compute()
conversation_result = conversation_df.compute()

# Close the database connection
conn.close()

# Display the results
print("Language detection results for issues:")
print(issues_result[['id', 'title_language', 'body_language']])

print("\nLanguage detection results for conversations:")
print(conversation_result[['id', 'Prompt_language', 'Answer_language']])
