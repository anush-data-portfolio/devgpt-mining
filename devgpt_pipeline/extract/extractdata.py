'''
This file is used to extract data from the snapshots in the data folders store them in a csv file.
The extracted data is stored in the 'extracted' folder.
'''
import os
import json
import pandas as pd
from devgpt_pipeline.extract.utls import (
    get_files_in_folder, parse_json, get_snapshot_folders)
from pipeline import Component

class DataExtractor(Component):
    '''
    Extract data from the snapshots in the data folder
    '''
    def __init__(self, data_folder='data'):
        super().__init__('Extract')
        self.data_folder = data_folder
        self.legend = {}
        self.file_type = [  'issue', 'pr', 'commit', 'hn', 'discussion', 'commit']
        self.file_df = {}
        self.unique_keys = {
            'issue': ['RepoName', 'Number', 'Title', 'Body'],
            'pr': ['RepoName', 'Number', 'Title', 'Body'],
            'commit': ['Sha', 'Message'],
            'hn': ['ID', 'Title'],
            'discussion': ['RepoName', 'Number', 'Title', 'Body'],
            'sharing': ['type_id', 'share_no', 'Title'],
            'conversation': ['sharing_id', 'position', 'Prompt', 'Answer']
        }
        self.distribution = {}  # check the frequency of unique keys across snapshots

    def process(self):
        '''
        Run the extraction process
        '''
        print("Starting Extraction")
        self.__combine_all_files()
        self.__create_unique_keys()
        self.__extract_sharing()
        self.__extract_chatgpt()
        self.__check_for_frequency()

        path = 'extracted'
        if not os.path.exists('extracted'):
            os.makedirs('extracted')
        for key, df in self.file_df.items():
            df.to_csv(f'{path}/{key}.csv', index=False)
        # store snapshot legend
        with open(f'{path}/legend.json', encoding='utf-8', mode='w') as f:
            json.dump(self.legend, f)
        if not os.path.exists(f'{path}/distribution'):
            os.makedirs(f'{path}/distribution')
        for key, df in self.distribution.items():
            df.to_csv(f'{path}/distribution/{key}.csv', index=False)

    def __get_all_files(self):
        folders = get_snapshot_folders(self.data_folder)
        for ftype in self.file_type:
            self.file_df[ftype] = []
            for folder in folders:
                self.file_df[ftype].append(get_files_in_folder(folder, ftype))

    def __create_unique_keys(self):
        for table, df in self.file_df.items():
            self.__create_unique_key(table)



    def __create_unique_key(self, table):
        df = self.file_df[table]
        df['uid'] = ''
        for col in self.unique_keys[table]:
            df['uid'] += '_' + df[col].astype(str)
            df['uid'] = df['uid'].apply(lambda x: hash(x))
            df['uid'] = df['uid'].astype(str)
        df.drop_duplicates(subset=['uid', 'snapshot'], inplace=True)
        self.file_df[table] = df

    def __check_for_frequency(self):
        for key, df in self.file_df.items():
            temp = df.groupby('uid')['snapshot'].apply(list).reset_index()
            temp['frequency'] = temp['snapshot'].apply(len)
            temp['has_7'] = temp['snapshot'].apply(lambda x: 1 if len(set(x)) == 7 else 0)
            self.distribution[key] = temp

    def __extract_sharing(self):
        sharing_data = []
        for key, df in self.file_df.items():
            for _, row in df.iterrows():
                if 'ChatgptSharing' in row:
                    sharing_d = pd.DataFrame(row['ChatgptSharing'])
                    for i, share_row in sharing_d.iterrows():
                        temp = pd.DataFrame([share_row])
                        temp['type'] = key
                        temp['type_id'] = row['uid']
                        temp['share_no'] = i
                        temp['snapshot'] = str(row['snapshot'])
                        sharing_data.append(temp)
        for df in self.file_df.values():
            df.drop(columns=['ChatgptSharing'], inplace=True)
        sharingdf = pd.concat(sharing_data, ignore_index=True)
        self.file_df['sharing'] = sharingdf
        self.__create_unique_key('sharing')



    def __extract_chatgpt(self):
        conversationdf = pd.DataFrame()
        conversations = []
        for _, row in self.file_df['sharing'].iterrows():
            row['Conversations'] = [] if isinstance(
                row['Conversations'], float
                ) else row['Conversations']
            sharing_id, snapshot = row['uid'], row['snapshot']
            pos = 0
            for conv in row['Conversations']:
                conv['ListOfCode'] = str(conv['ListOfCode'])
                temp = pd.DataFrame([conv])
                temp['position'] = pos
                temp['sharing_id'] = sharing_id
                temp['snapshot'] = snapshot
                conversations.append(temp)
                pos += 1
        conversationdf = pd.concat(conversations, ignore_index=True)
        self.file_df['conversation'] = conversationdf
        self.__create_unique_key('conversation')

    def __combine_all_files(self):
        self.__get_all_files()

        for key, files in self.file_df.items():
            index = 1
            df = pd.DataFrame()
            for _, file in enumerate(files):
                folder = file.split('/')[1]
                keys = self.legend.keys()
                if folder not in keys:
                    self.legend[folder] = index
                data = parse_json(file)
                temp = pd.DataFrame(data)
                temp['snapshot'] = index
                df = pd.concat([df, temp])
                index += 1
            self.file_df[key] = df
