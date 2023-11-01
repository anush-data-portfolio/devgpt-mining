from sqlalchemy import create_engine
from devgpt_processing.load.model import Conversation, Issue, PullRequest
from sqlalchemy.orm import sessionmaker
import sqlalchemy
import pandas as pd

def search_and_save_to_csv(model, columns, key_word):
    # Create a SQLite database connection and session
    engine = create_engine('sqlite:///devgpt.sqlite')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Define the model and get the table name
    table_name = model.__table__.name

    # Build the filter conditions for each column
    filters = [getattr(model, column).ilike(f'%{key_word}%') for column in columns]  # Use ilike for case-insensitive search
    filter_condition = filters[0] if len(filters) == 1 else sqlalchemy.or_(*filters)

    # Use a single query to filter rows with the keyword in any of the specified columns
    rows = session.query(model).filter(filter_condition).all()

    # Create a DataFrame directly from the query result
    df = pd.read_sql(session.query(model).filter(filter_condition).statement, session.bind)
    keywords = key_word.replace(' ', '_')
    keywords = key_word.replace('/', '_')

    # Define the CSV file name based on the keyword and table name
    csv_filename = f'subset/{key_word}_{table_name}.csv'

    # Save the DataFrame to a CSV file
    # df.to_csv(csv_filename, index=False)

    # Calculate the percentage of matching rows
    total_rows = session.query(model).count()
    matching_rows = len(rows)
    percentage = (matching_rows / total_rows) * 100 if total_rows > 0 else 0

    return {
        'table_name': table_name,
        'keyword': key_word,
        'percentage': percentage
    }


def search_and_save_stats_to_csv(models, keywords):
    stats_df = pd.DataFrame(columns=['table_name', 'keyword', 'percentage'])
    stats = []

    for model, columns in models:
        for keyword in keywords:
            results = search_and_save_to_csv(model, columns, keyword)
            stats_dict = {
                'table_name': results['table_name'],
                'keyword': results['keyword'],
                'percentage': results['percentage']
            }
            stats.append(stats_dict)
    
    # list of dictionaries to DataFrame
    stats_df = pd.DataFrame(stats)


    stats_filename = 'stats.csv'
    stats_df.to_csv(stats_filename, index=False)

# Define the models and their respective columns
models = [
    (Conversation, ['Prompt', 'Answer']),
    (Issue, ['body', 'title']),
    (PullRequest, ['body', 'title'])
]

# clear subset folder
import os
import shutil
folder = 'subset'
for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print(f'Failed to delete {file_path}. Reason: {e}')

# Define the keywords
keywords_file = "keywords.csv"
keywords_df = pd.read_csv(keywords_file)
keywords = keywords_df['keyword'].tolist()
# lower and strip whitespace
keywords = [keyword.lower().strip() for keyword in keywords]
# Call the new function to search and save stats



search_and_save_stats_to_csv(models, keywords)

