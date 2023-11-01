from devgpt_processing.extract.extractdata import ExtractData
from devgpt_processing.load.model import (
    Issue, Snapshot, Sharing, Conversation,
    PullRequest, Commit)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd

class DataLoader:
    def __init__(self, database_url):
        # self.data = ExtractData()
        # self.load = self.data.extract_frames()
        # self.snapshots = self.data.legend
        self.data_dict = {}
        self.engine = create_engine(database_url)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def clear_tables(self):
        # self.session.query(Snapshot).delete() since they dont change do not delete
        self.session.query(Sharing).delete()
        self.session.query(Conversation).delete()
        self.session.query(Issue).delete()
        self.session.commit()

    def load_snapshots(self):
        for id, snapshot in self.snapshots.items():
            row = Snapshot(snapshot=id, id=snapshot)
            self.session.add(row)
        self.session.commit()

    def load_prs(self):
        pr_list = []
        for _, row in self.data_dict['pr'].iterrows():
            row_dict = row.to_dict()
            row_dict = {k.lower(): v for k, v in row_dict.items()}
            pr = self.parse_pr(row_dict)
            if pr is None:
                continue
            pr_list.append(pr)
        
        pr_list = list(set(pr_list))
        self.session.add_all(pr_list)
        self.session.commit()
    
    def parse_pr(self, pr):

        check = self.session.query(PullRequest.id).filter(PullRequest.id == pr['key']).first()
        if check is not None:
            return None
        pr_close = pr['closedat'],
        
        if pr['closedat'] is None:
            pr_close = ""
        pr_obj = PullRequest(
            id=pr['key'],
            url=pr['url'],
            author=pr['author'],
            repo_name=pr['reponame'],
            repo_language=pr['repolanguage'],
            number=pr['number'],
            title=pr['title'],
            body=pr['body'],
            created_at=str(pr['createdat']),
            updated_at=str(pr['updatedat']),
            merged_at=str(pr['mergedat']),
            closed_at=str(pr_close),
            state=pr['state'],
            snapshot_id=pr['snapshot'],
            additions=pr['additions'],
            deletions=pr['deletions'],
            changed_files=pr['changedfiles'],
            commits_total_count=pr['commitstotalcount'],

        )
        return pr_obj
    
    def parse_issue(self, issue):
        check = self.session.query(Issue.id).filter(Issue.id == issue['key']).first()
        if check is not None:
            return None
        if issue['closedat'] is None:
            iss = ""
        else:
            iss = issue['closedat'],
        issue_obj = Issue(
            id=issue['key'],
            url=issue['url'],
            author=issue['author'],
            repo_name=issue['reponame'],
            repo_language=issue['repolanguage'],
            number=issue['number'],
            title=issue['title'],
            body=issue['body'],
            created_at=str(issue['createdat']),
            updated_at=str(issue['updatedat']),
            closed_at=str(iss),
            state=issue['state'],
            snapshot_id=issue['snapshot']
        )
        return issue_obj    

    def load_issues(self):
        issue_list = []
        for _, row in self.data_dict['issue'].iterrows():
            row_dict = row.to_dict()
            row_dict = {k.lower(): v for k, v in row_dict.items()}
            issue = self.parse_issue(row_dict)
            if issue is None:
                continue
            issue_list.append(issue)
        
        issue_list = list(set(issue_list))
        self.session.add_all(issue_list)
        self.session.commit()

    def parse_sharing(self, sharing):
        fk_id = None
        sharing_data = {
            'id': sharing['id'],
            'snapshot_id': sharing['snapshot'],
            'url': sharing['url'],
            'mentions': str(sharing['mention']),
            'status': sharing['status'],
            'numberofprompts': sharing['numberofprompts'],
            'title': sharing['title'],
            'dateofconversation': sharing['dateofconversation'],
            'dateofaccess': sharing['dateofaccess'],
            'type': sharing['type'],
        }
        if sharing['type'] == 'issue':
            fk_id = self.session.query(Issue.id).filter(Issue.id == sharing['key']).first()
            sharing_data['issue_id'] = fk_id[0]
        if sharing['type'] == 'pr':
            fk_id = self.session.query(PullRequest.id).filter(PullRequest.id == sharing['key']).first()
            sharing_data['pull_request_id'] = fk_id[0]
        sharing_instance = Sharing(**sharing_data)
        return sharing_instance

    def load_sharing(self):
        for _, row in self.data_dict['sharing'].iterrows():
            row_dict = row.to_dict()
            row_dict = {k.lower(): v for k, v in row_dict.items()}
            sharing = self.parse_sharing(row_dict)
            if sharing is not None:
                self.session.add(sharing)
        self.session.commit()

    def parse_conversation(self, conversation):
        sharing_id = self.session.query(Sharing.id).filter(Sharing.id == conversation['sharing_id']).first()
        if sharing_id is None:
            return None
        conversation_data = {
            'Prompt': conversation['Prompt'],
            'ListOfCode': conversation['ListOfCode'],
            'Answer': conversation['Answer'],
            'position': conversation['position'],
            'sharing_id': sharing_id[0]
        }
        conversation_instance = Conversation(**conversation_data)
        return conversation_instance

    def load_conversations(self):
        for _, row in self.data_dict['conversation'].iterrows():
            row_dict = row.to_dict()
            conversation = self.parse_conversation(row_dict)
            if conversation is not None:
                self.session.add(conversation)
        self.session.commit()
    
    def save_data_dict(self):
        # import the extracted data into csv files
        folder = "data/extracted"
        for key, df in self.data_dict.items():
            df.to_csv(f"{folder}/{key}.csv", index=False)
        print("Data saved")
    
    def get_data_dict(self, folder="data/extracted", keys=None):
        for key in keys:
            import os 
            if not os.path.exists(f"{folder}/{key}.csv"):
                raise Exception(f"File {folder}/{key}.csv does not exist")
            self.data_dict[key] = pd.read_csv(f"{folder}/{key}.csv")
        return self.data_dict


    def load_data(self):
        keys = ['pr', 'issue', 'sharing', 'conversation', 'discussion', 'hn']
        self.data_dict = self.get_data_dict(keys=keys)

        print('Loading data...')
        self.clear_tables()
        print('Tables cleared')
        # self.load_snapshots()
        # print('Snapshots loaded')
        self.load_issues()
        print('Issues loaded')
        self.load_prs()
        print('Pull requests loaded')
        self.load_sharing()
        print('Sharing loaded')
        self.load_conversations()
        print('Conversations loaded')

if __name__ == "__main__":
    database_url = 'sqlite:///devgpt.sqlite'  # Update this with your database URL
    data_loader = DataLoader(database_url)
    data_loader.load_data()
