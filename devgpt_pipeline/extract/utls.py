'''
File Utils

'''
import os
import json

def get_snapshot_folders(root):
    '''
    Get all folders starting with 'snapshot' in the data folder
    '''
    folders = os.listdir(root)
    # Get folders starting with 'snapshot'
    folders = [f for f in folders if f.startswith('snapshot')]
    # sort the folders
    folders = sorted(folders)
    return folders

def get_snapshot_numbers(folder):
    '''
    Get the snapshot number from the folder name
    '''
    # split the folder name by '_'
    folder = folder.split('_')
    # get the last element
    folder = folder[-1]
    # convert to integer
    folder = int(folder)
    return folder



def get_files_in_folder(folder, ftype):
    '''
    Get files in a folder
    '''
    files = os.listdir('data/' + folder)
    # check for files containing 'issue' in the name
    files = [f for f in files if ftype in f]
    # merge folder name with file name
    files = ['data/' + folder + '/' + f for f in files]
    return files[0]



def parse_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data['Sources']
