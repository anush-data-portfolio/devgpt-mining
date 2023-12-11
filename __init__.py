from devgpt_pipeline.load.data_loader import DataLoader

if __name__ == "__main__":
    database_url = 'sqlite:///devgpt.sqlite'  # Update this with your database URL
    data_loader = DataLoader(database_url)
    data_loader.load_data()