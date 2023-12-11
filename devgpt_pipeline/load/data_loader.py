from devgpt_pipeline.models.model import (
    Issue, Snapshot, Sharing, Conversation,HackerNews,
    PullRequest, Discussion, Commit, Base )
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os
import json
from pipeline import Component
from alembic.config import Config


class DataLoader(Component):
    def __init__(self):
        super().__init__('Load')
        self.extract_folder = 'extracted'
        self.snapshots = {}
        self.database_url = "sqlite:///devgpt.sqlite"
        self.data_dict = {}
        self.engine = create_engine(self.database_url)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def __create_db(self):
        # create a sqlite database
        Base.metadata.create_all(self.engine)

    def __check_db_exists(self):
        if not os.path.exists('devgpt.sqlite'):
            self.__create_db()
    
    def process(self):
        self.__check_db_exists()
        keys = ['commit', 'discussion', 'issue', 'pr', 'sharing', 'conversation', 'hn']
        self.__set_snapshot_legend()
        self.__set_data_dict(keys)

        print('Loading data...')
        self.clear_tables() 
        print('Tables cleared')
        snapshots = self.load_snapshots()
        print(f'{snapshots} snapshots loaded')
        prs = self.load_prs()
        print(f'{prs} pull requests loaded')
        issues = self.load_issues()
        print(f'{issues} issues loaded')
        hns = self.load_hn()
        print(f'{hns} hacker news loaded')
        discussions = self.load_discussions()
        print(f'{discussions} discussions loaded')
        commits = self.load_commits()
        print(f'{commits} commits loaded')
        sharings = self.load_sharing()
        print(f'{sharings} sharings loaded')
        conversations = self.load_conversations()
        print(f'{conversations} conversations loaded')

        print('Data loaded')

    def __set_data_dict(self,keys=None):
        for key in keys:
            import os 
            if not os.path.exists(f"{self.extract_folder}/{key}.csv"):
                raise Exception(f"File {self.extract_folder}/{key}.csv does not exist")
            self.data_dict[key] = pd.read_csv(f"{self.extract_folder}/{key}.csv")
            os.remove(f"{self.extract_folder}/{key}.csv")


    
    def __set_snapshot_legend(self):
        with open(f'{self.extract_folder}/legend.json', 'r') as f:
            self.snapshots = json.load(f)


    def clear_tables(self):
        self.session.query(Snapshot).delete() #since they dont change do not delete
        self.session.query(Sharing).delete()
        self.session.query(Conversation).delete()
        self.session.query(Discussion).delete()
        self.session.query(PullRequest).delete()
        self.session.query(Issue).delete()
        self.session.query(Commit).delete()
        self.session.query(HackerNews).delete()
        self.session.commit()

    def load_snapshots(self):
        for id, snapshot in self.snapshots.items():
            row = Snapshot(snapshot=id, id=snapshot)
            self.session.add(row)
        self.session.commit()
        return len(self.snapshots)

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
        return len(pr_list)

    def parse_pr(self, pr):
        check = self.session.query(PullRequest.id).filter(PullRequest.id == pr['uid']).first()
        if check is not None:
            return None
        pr_close = pr['closedat'],

        if pr['closedat'] is None:
            pr_close = ""
        pr_obj = PullRequest(
            id=pr['uid'],
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
        check = self.session.query(Issue.id).filter(Issue.id == issue['uid']).first()
        if check is not None:
            return None
        if issue['closedat'] is None:
            iss = ""
        else:
            iss = issue['closedat'],
        issue_obj = Issue(
            id=issue['uid'],
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
        return len(issue_list)

    def parse_sharing(self, sharing):
        fk_id = None
        sharing_data = {
            'id': sharing['uid'],
            'snapshot_id': sharing['snapshot'],
            'url': sharing['url'],
            'mentions': str(sharing['mention']),
            'status': sharing['status'],
            'numberofprompts': sharing['numberofprompts'],
            'title': sharing['title'],
            'dateofconversation': sharing['dateofconversation'],
            'dateofaccess': sharing['dateofaccess'],
            'type': sharing['type'],
            'number': sharing['share_no'],
        }
        if sharing['type'] == 'issue':
            fk_id = self.session.query(Issue.id).filter(Issue.id == sharing['type_id']).first()
            sharing_data['issue_id'] = fk_id[0]
        if sharing['type'] == 'pr':
            fk_id = self.session.query(PullRequest.id).filter(PullRequest.id == sharing['type_id']).first()
            sharing_data['pull_request_id'] = fk_id[0]
        if sharing['type'] == 'discussion':
            fk_id = self.session.query(Discussion.id).filter(Discussion.id == sharing['type_id']).first()
            sharing_data['discussion_id'] = fk_id[0]
        if sharing['type'] == 'commit':
            fk_id = self.session.query(Commit.id).filter(Commit.id == sharing['type_id']).first()
            sharing_data['commit_id'] = fk_id[0]



        sharing_instance = Sharing(**sharing_data)
        return sharing_instance

    def load_sharing(self):
        sharing_list = []
        for _, row in self.data_dict['sharing'].iterrows():
            row_dict = row.to_dict()
            row_dict = {k.lower(): v for k, v in row_dict.items()}
            sharing = self.parse_sharing(row_dict)
            if sharing is not None:
                sharing_list.append(sharing)
        sharing_list = list(set(sharing_list))
 
        self.session.add_all(sharing_list)
        self.session.commit()
        return len(sharing_list)

    def parse_conversation(self, conversation):
        sharing_id = self.session.query(Sharing.id).filter(Sharing.id == conversation['sharing_id']).first()
        if sharing_id is None:
            return None
        conversation_data = {
            'id': conversation['uid'],
            'position': conversation['position'],
            'Prompt': conversation['prompt'],
            'ListOfCode': conversation['listofcode'],
            'Answer': conversation['answer'],
            'sharing_id': sharing_id[0],
            'snapshot_id': conversation['snapshot'],

        }
        conversation_instance = Conversation(**conversation_data)
        return conversation_instance

    def load_conversations(self):
        conversation_list = []
        for _, row in self.data_dict['conversation'].iterrows():
            row_dict = row.to_dict()
            row_dict = {k.lower(): v for k, v in row_dict.items()}
            conversation = self.parse_conversation(row_dict)
            if conversation is not None:
                conversation_list.append(conversation)
        conversation_list = list(set(conversation_list))
        self.session.add_all(conversation_list)
        self.session.commit()
        return len(conversation_list)

    def parse_discussion(self, discussion):
        discussion_data = {
            'id': discussion['uid'],
            'url': discussion['url'],
            'author': discussion['author'],
            'repo_name': discussion['reponame'],
            'repo_language': discussion['repolanguage'],
            'number': discussion['number'],
            'title': discussion['title'],
            'body': discussion['body'],
            'created_at': str(discussion['createdat']),
            'updated_at': str(discussion['updatedat']),
            'closed_at': str(discussion['closedat']),
            'closed': discussion['closed'],
            'upvotes': discussion['upvotecount'],
            'snapshot_id': discussion['snapshot'],
        }
        discussion_instance = Discussion(**discussion_data)
        return discussion_instance
    
    def load_discussions(self):
        discussion_list = []
        for _, row in self.data_dict['discussion'].iterrows():
            row_dict = row.to_dict()
            row_dict = {k.lower(): v for k, v in row_dict.items()}
            discussion = self.parse_discussion(row_dict)
            if discussion is not None:
                discussion_list.append(discussion)
        discussion_list = list(set(discussion_list))
        self.session.add_all(discussion_list)
        self.session.commit()
        return len(discussion_list)
    
    def parse_commit(self, commit):
        commit_data = {
            'id': commit['uid'],
            'url': commit['url'],
            'author': commit['author'],
            'repo_name': commit['reponame'],
            'repo_language': commit['repolanguage'],
            'sha': commit['sha'],
            'message': commit['message'],
            'commit_at': str(commit['commitat']),
            'author_at': str(commit['authorat']),
            'snapshot_id': commit['snapshot'],
        }
        commit_instance = Commit(**commit_data)
        return commit_instance
    
    def load_commits(self):
        commit_list = []
        for _, row in self.data_dict['commit'].iterrows():
            row_dict = row.to_dict()
            row_dict = {k.lower(): v for k, v in row_dict.items()}
            commit = self.parse_commit(row_dict)
            if commit is not None:
                commit_list.append(commit)
        commit_list = list(set(commit_list))
        self.session.add_all(commit_list)
        self.session.commit()
        return len(commit_list)

    def parse_hn(self, hn):
        hn_data = {
            'id': hn['uid'],
            'url': hn['attachedurl'],
            'author': hn['author'],
            'title': hn['title'],
            'created_at': str(hn['createdat']),
            'snapshot_id': hn['snapshot'],
        }
        hn_instance = HackerNews(**hn_data)
        return hn_instance
    
    def load_hn(self):
        hn_list = []
        for _, row in self.data_dict['hn'].iterrows():
            row_dict = row.to_dict()
            row_dict = {k.lower(): v for k, v in row_dict.items()}
            hn = self.parse_hn(row_dict)
            if hn is not None:
                hn_list.append(hn)
        hn_list = list(set(hn_list))
        self.session.add_all(hn_list)
        self.session.commit()
        return len(hn_list)



