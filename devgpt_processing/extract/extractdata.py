from devgpt_processing.extract.utls import get_files_in_folder, parse_json, get_snapshot_folders
import pandas as pd


class ExtractData:
    '''
    Extract data from the snapshot files
    '''

    def __init__(self, data_folder = 'data') -> None:
        self.legend = {}
        self.file_type=['discussion'] #'issue', 'pr', 'commit', 'hn', 
        self.file_df = {}
        self.data_folder = data_folder
        self.unique_keys = {
                                'issue' : ['RepoName', 'Number', 'snapshot', 'Title'],
                                'pr' :  ['RepoName', 'Number', 'snapshot', 'Title'],
                                'commit' : ['Sha', 'snapshot'],
                                'hn' : ['ID', 'snapshot', 'Title'],
                                'discussion' :  ['RepoName', 'Number', 'snapshot', 'Title'],
                            }
        self.distribution  = {} # check the frequency of unique keys across snapshots

    def __get_all_files(self):
        folders = get_snapshot_folders(self.data_folder)
        for ftype in self.file_type:
            self.file_df[ftype] = []
            for folder in folders:
                self.file_df[ftype].append(get_files_in_folder(folder, ftype))
    
    def __create_unique_keys(self):
        for _, df in self.file_df.items():
            df['key'] = ''
            for col in self.unique_keys[_]:
                df['key'] += '_'+ df[col].astype(str)
            # make a unique key by hashing
            df['key'] = df['key'].apply(lambda x: hash(x))
            # remove duplicates
            df.drop_duplicates(subset=['key'], inplace=True)
    
    def __check_for_frequency(self):
        for key, df in self.file_df.items():
            temp = df.groupby(level=0)['snapshot'].apply(list).reset_index()
            temp['frequency'] = temp['snapshot'].apply(lambda x: len(x))
            temp['has_7'] = temp['snapshot'].apply(lambda x: 1 if len(set(x)) == 7 else 0)
            self.distribution[key] = temp
    
    def __extract_sharing(self):
        '''
        Extract sharing between snapshots
        '''
        sharingdf = pd.DataFrame()

        for _, df in self.file_df.items():
            for i, row in df.iterrows():
                temp = pd.DataFrame(row['ChatgptSharing'])
                temp['snapshot'] = row['snapshot']
                temp['key'] =  row['key']
                temp['type'] = _
                sharingdf = pd.concat([sharingdf, temp])
        df.drop(columns=['ChatgptSharing'], inplace=True)
        sharingdf['id'] = sharingdf['key'].astype(str) + '_' + sharingdf['snapshot'].astype(str) + '_' + sharingdf.groupby('key').cumcount().astype(str)

        self.file_df['sharing'] = sharingdf
    
    def __extract_chatgpt(self):
        conversationdf = pd.DataFrame()
        for _, row in self.file_df['sharing'].iterrows():
            row['Conversations'] = [] if type(row['Conversations']) == float else row['Conversations']
            key, snapshot = row.name, row['snapshot']
            pos = 0
            for conv in row['Conversations']:
                conv['ListOfCode'] = str(conv['ListOfCode'])
                temp = pd.DataFrame([conv])
                temp['key'] = key 
                temp['position'] = pos
                temp['snapshot'] = snapshot
                temp['sharing_id'] = row['id']
                conversationdf = pd.concat([conversationdf, temp])
                pos += 1
        self.file_df['conversation'] = conversationdf

    def __combine_all_files(self):
        '''
        Combine all files in one list
        '''
        self.__get_all_files()
        
        for key, files in self.file_df.items():
            index = 1
            df = pd.DataFrame()
            # if folder not in legend keys
            for i, file in enumerate(files):
                folder = file.split('/')[1]
                if folder not in self.legend.keys():
                    self.legend[folder] = index
                data = parse_json(file)
                temp = pd.DataFrame(data)
                temp['snapshot'] = index
                df = pd.concat([df, temp])
                index += 1
            self.file_df[key] = df

    def extract_frames(self):
        '''
        Extract all the frames
        '''
        self.__combine_all_files()
        self.__create_unique_keys()
        print('Unique keys created')
        self.__extract_sharing()
        self.__extract_chatgpt()
        print('Sharing and Chatgpt extracted')
        self.__check_for_frequency()

        return self.file_df
    

