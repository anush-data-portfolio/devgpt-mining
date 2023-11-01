# sqlalchmy models for transform database

from sqlalchemy import Column, Integer, String, Float, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

'''
Issue has a one-to-many relationship with sharing
pull_request has a one-to-many relationship with sharing
commit has a one-to-many relationship with sharing
history has a one-to-many relationship with sharing
discussion has a one-to-many relationship with sharing
Sharing has a many-to-many relationship with conversation

# the data is a snapshot of the issue at a particular time with 7 snapshots

'''




class Snapshot(Base):
    __tablename__ = 'snapshot'
    id = Column(Integer, primary_key=True)
    snapshot = Column(String)

class PullRequest(Base):
    __tablename__ = 'pull_request'
    id = Column(Integer, primary_key=True)
    url = Column(String)
    author = Column(String)
    repo_name = Column(String)
    repo_language = Column(String)
    language= Column(String, nullable=True)
    number = Column(Integer)
    title = Column(String)
    body = Column(String)
    created_at = Column(String)
    closed_at = Column(String)
    merged_at = Column(String)
    updated_at = Column(String)
    state = Column(String)
    additions = Column(Integer)
    deletions = Column(Integer)
    changed_files = Column(Integer)
    commits_total_count = Column(Integer)
    commit_sha = Column(String)
    snapshot_id = Column(Integer, ForeignKey('snapshot.id'))
    snapshot = relationship("Snapshot", backref="pull_request")
    sharing = relationship("Sharing", backref="pull_request")

class Commit(Base):
    __tablename__ = 'commit'
    id = Column(Integer, primary_key=True)
    url = Column(String)
    language= Column(String, nullable=True)
    author = Column(String)
    repo_name = Column(String)
    repo_language = Column(String)
    number = Column(Integer)
    title = Column(String)
    body = Column(String)
    created_at = Column(String)
    closed_at = Column(String)
    merged_at = Column(String)
    updated_at = Column(String)
    state = Column(String)
    additions = Column(Integer)
    deletions = Column(Integer)
    changed_files = Column(Integer)
    commits_total_count = Column(Integer)
    commit_sha = Column(String)
    snapshot_id = Column(Integer, ForeignKey('snapshot.id'))
    snapshot = relationship("Snapshot", backref="commit")
    sharing = relationship("Sharing", backref="commit")


class Issue(Base):
    __tablename__ = 'issue'
    id = Column(String, primary_key=True, autoincrement=False)
    url = Column(String)
    author = Column(String)
    repo_name = Column(String)
    repo_language = Column(String)
    language= Column(String, nullable=True)
    number = Column(Integer)
    title = Column(String)
    body = Column(String)
    created_at = Column(String, nullable=True)
    closed_at = Column(String, nullable=True)
    updated_at = Column(String, nullable=True)
    state = Column(String)
    snapshot_id = Column(Integer, ForeignKey('snapshot.id'))
    snapshot = relationship("Snapshot", backref="issue")
    sharing = relationship("Sharing", backref="issue")

class Discussion(Base):
    __tablename__ = 'discussion'
    id = Column(Integer, primary_key=True)
    url = Column(String)
    author = Column(String)
    repo_name = Column(String)
    repo_language = Column(String)
    language= Column(String, nullable=True)
    number = Column(Integer)
    title = Column(String)
    body = Column(String)
    created_at = Column(String)
    closed_at = Column(String)
    updated_at = Column(String)
    

class Sharing(Base):
    __tablename__ = 'sharing'
    id = Column(String, primary_key=True)
    snapshot_id = Column(Integer, ForeignKey('snapshot.id'))
    url = Column(String)
    mentions = Column(String)
    status = Column(String)
    numberofprompts = Column(Integer)
    title = Column(String)
    dateofconversation = Column(String, nullable=True)
    dateofaccess = Column(String, nullable=True)
    type = Column(String)
    issue_id = Column(String, ForeignKey('issue.id'), nullable=True, default=None)
    pull_request_id = Column(Integer, ForeignKey('pull_request.id'), nullable=True, default=None)
    commit_id = Column(Integer, ForeignKey('commit.id'), nullable=True, default=None)
    # discussion_id = Column(Integer, ForeignKey('discussion.id'), nullable=True, default=None)
    

class Conversation(Base):
    __tablename__ = 'conversation'
    id = Column(Integer, primary_key=True)
    Prompt = Column(String)
    Answer = Column(String)
    ListOfCode = Column(String)
    position = Column(Integer)
    # language_id = Column(Integer, ForeignKey('language.id'))
    # language = relationship("Language", backref="conversation")
    sharing_id = Column(String, ForeignKey('sharing.id'))
    sharing = relationship("Sharing", backref="conversation")
    language= Column(String, nullable=True)
    

