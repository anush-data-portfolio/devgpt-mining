# sqlalchmy models for transform database

from sqlalchemy import Column, Integer, String, Float, ForeignKey, String, Boolean, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr




'''
Issue has a one-to-many relationship with sharing
pull_request has a one-to-many relationship with sharing
commit has a one-to-many relationship with sharing
history has a one-to-many relationship with sharing
discussion has a one-to-many relationship with sharing
Sharing has a many-to-many relationship with conversation

# the data is a snapshot of the issue at a particular time with 7 snapshots

'''



# define id and snapshot as composite primary key in base class
decBase = declarative_base()

class Language(decBase):
    __tablename__ = 'language'
    name = Column(String)
    code = Column(String, primary_key=True)

class Snapshot(decBase):
    __tablename__ = 'snapshot'
    id = Column(String, primary_key=True)
    snapshot = Column(String)

class Base(decBase):
    __abstract__ = True

    id = Column(String)
    snapshot_id = Column(String, ForeignKey('snapshot.id'))
    language_id = Column(String, ForeignKey('language.code'),nullable=True)
    @declared_attr
    def snapshot(cls):
        return relationship('Snapshot')
    @declared_attr
    def __table_args__(cls):
        return (PrimaryKeyConstraint('id', 'snapshot_id'),)
    @declared_attr
    def language(cls):
        return relationship('Language')
        


class PullRequest(Base):
    __tablename__ = 'pull_request'
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
    sharing = relationship("Sharing", backref="pull_request")

class Commit(Base):
    __tablename__ = 'commit'
    url = Column(String)
    language= Column(String, nullable=True)
    author = Column(String)
    repo_name = Column(String)
    repo_language = Column(String)
    message = Column(String)
    commit_at = Column(String)
    author_at = Column(String)
    sha = Column(String)
    sharing = relationship("Sharing", backref="commit")


class Issue(Base):
    __tablename__ = 'issue'
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
    sharing = relationship("Sharing", backref="issue")

class Discussion(Base):
    __tablename__ = 'discussion'
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
    closed = Column(Boolean)
    upvotes = Column(Integer)
    sharing = relationship("Sharing", backref="discussion")
    

class Sharing(Base):
    __tablename__ = 'sharing'
    number = Column(Integer)
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
    discussion_id = Column(Integer, ForeignKey('discussion.id'), nullable=True, default=None)

class Conversation(Base):
    __tablename__ = 'conversation'
    Prompt = Column(String)
    Answer = Column(String)
    ListOfCode = Column(String)
    position = Column(Integer)
    # language_id = Column(Integer, ForeignKey('language.id'))
    # language = relationship("Language", backref="conversation")
    sharing_id = Column(String, ForeignKey('sharing.id'))
    sharing = relationship("Sharing", backref="conversation")
    language= Column(String, nullable=True)

class HackerNews(Base):
    __tablename__ = 'hackernews'
    url = Column(String)
    title = Column(String)
    author = Column(String)
    created_at = Column(String)
    upvotes = Column(Integer)
    language= Column(String, nullable=True)
    sharing = relationship("Sharing", backref="hackernews")
    sharing_id = Column(String, ForeignKey('sharing.id'))


class KeywordMatch(decBase):
    __tablename__ = 'keywordmatch'
    keyword = Column(String)
    id = Column(String)
    snapshot_id = Column(String, ForeignKey('snapshot.id'))
    column_name = Column(String)
    table = Column(String)

    @declared_attr
    def snapshot(cls):
        return relationship('Snapshot')
    @declared_attr
    def __table_args__(cls):
        return (PrimaryKeyConstraint('id', 'snapshot_id', 'keyword', 'column_name'),)
    

    # dummy df with 10 rows, keyword , id, snapshot_id, column_name, table

    
