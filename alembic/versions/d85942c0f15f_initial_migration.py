"""initial migration

Revision ID: d85942c0f15f
Revises: 
Create Date: 2023-11-29 18:44:30.841076

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd85942c0f15f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('language',
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('code', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('code')
    )
    op.create_table('snapshot',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('snapshot', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('commit',
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('language', sa.String(), nullable=True),
    sa.Column('author', sa.String(), nullable=True),
    sa.Column('repo_name', sa.String(), nullable=True),
    sa.Column('repo_language', sa.String(), nullable=True),
    sa.Column('message', sa.String(), nullable=True),
    sa.Column('commit_at', sa.String(), nullable=True),
    sa.Column('author_at', sa.String(), nullable=True),
    sa.Column('sha', sa.String(), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('snapshot_id', sa.String(), nullable=False),
    sa.Column('language_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['language_id'], ['language.code'], ),
    sa.ForeignKeyConstraint(['snapshot_id'], ['snapshot.id'], ),
    sa.PrimaryKeyConstraint('id', 'snapshot_id')
    )
    op.create_table('discussion',
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('author', sa.String(), nullable=True),
    sa.Column('repo_name', sa.String(), nullable=True),
    sa.Column('repo_language', sa.String(), nullable=True),
    sa.Column('language', sa.String(), nullable=True),
    sa.Column('number', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('body', sa.String(), nullable=True),
    sa.Column('created_at', sa.String(), nullable=True),
    sa.Column('closed_at', sa.String(), nullable=True),
    sa.Column('updated_at', sa.String(), nullable=True),
    sa.Column('closed', sa.Boolean(), nullable=True),
    sa.Column('upvotes', sa.Integer(), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('snapshot_id', sa.String(), nullable=False),
    sa.Column('language_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['language_id'], ['language.code'], ),
    sa.ForeignKeyConstraint(['snapshot_id'], ['snapshot.id'], ),
    sa.PrimaryKeyConstraint('id', 'snapshot_id')
    )
    op.create_table('issue',
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('author', sa.String(), nullable=True),
    sa.Column('repo_name', sa.String(), nullable=True),
    sa.Column('repo_language', sa.String(), nullable=True),
    sa.Column('language', sa.String(), nullable=True),
    sa.Column('number', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('body', sa.String(), nullable=True),
    sa.Column('created_at', sa.String(), nullable=True),
    sa.Column('closed_at', sa.String(), nullable=True),
    sa.Column('updated_at', sa.String(), nullable=True),
    sa.Column('state', sa.String(), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('snapshot_id', sa.String(), nullable=False),
    sa.Column('language_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['language_id'], ['language.code'], ),
    sa.ForeignKeyConstraint(['snapshot_id'], ['snapshot.id'], ),
    sa.PrimaryKeyConstraint('id', 'snapshot_id')
    )
    op.create_table('pull_request',
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('author', sa.String(), nullable=True),
    sa.Column('repo_name', sa.String(), nullable=True),
    sa.Column('repo_language', sa.String(), nullable=True),
    sa.Column('language', sa.String(), nullable=True),
    sa.Column('number', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('body', sa.String(), nullable=True),
    sa.Column('created_at', sa.String(), nullable=True),
    sa.Column('closed_at', sa.String(), nullable=True),
    sa.Column('merged_at', sa.String(), nullable=True),
    sa.Column('updated_at', sa.String(), nullable=True),
    sa.Column('state', sa.String(), nullable=True),
    sa.Column('additions', sa.Integer(), nullable=True),
    sa.Column('deletions', sa.Integer(), nullable=True),
    sa.Column('changed_files', sa.Integer(), nullable=True),
    sa.Column('commits_total_count', sa.Integer(), nullable=True),
    sa.Column('commit_sha', sa.String(), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('snapshot_id', sa.String(), nullable=False),
    sa.Column('language_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['language_id'], ['language.code'], ),
    sa.ForeignKeyConstraint(['snapshot_id'], ['snapshot.id'], ),
    sa.PrimaryKeyConstraint('id', 'snapshot_id')
    )
    op.create_table('sharing',
    sa.Column('number', sa.Integer(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('mentions', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('numberofprompts', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('dateofconversation', sa.String(), nullable=True),
    sa.Column('dateofaccess', sa.String(), nullable=True),
    sa.Column('type', sa.String(), nullable=True),
    sa.Column('issue_id', sa.String(), nullable=True),
    sa.Column('pull_request_id', sa.Integer(), nullable=True),
    sa.Column('commit_id', sa.Integer(), nullable=True),
    sa.Column('discussion_id', sa.Integer(), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('snapshot_id', sa.String(), nullable=False),
    sa.Column('language_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['commit_id'], ['commit.id'], ),
    sa.ForeignKeyConstraint(['discussion_id'], ['discussion.id'], ),
    sa.ForeignKeyConstraint(['issue_id'], ['issue.id'], ),
    sa.ForeignKeyConstraint(['language_id'], ['language.code'], ),
    sa.ForeignKeyConstraint(['pull_request_id'], ['pull_request.id'], ),
    sa.ForeignKeyConstraint(['snapshot_id'], ['snapshot.id'], ),
    sa.PrimaryKeyConstraint('id', 'snapshot_id')
    )
    op.create_table('conversation',
    sa.Column('Prompt', sa.String(), nullable=True),
    sa.Column('Answer', sa.String(), nullable=True),
    sa.Column('ListOfCode', sa.String(), nullable=True),
    sa.Column('position', sa.Integer(), nullable=True),
    sa.Column('sharing_id', sa.String(), nullable=True),
    sa.Column('language', sa.String(), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('snapshot_id', sa.String(), nullable=False),
    sa.Column('language_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['language_id'], ['language.code'], ),
    sa.ForeignKeyConstraint(['sharing_id'], ['sharing.id'], ),
    sa.ForeignKeyConstraint(['snapshot_id'], ['snapshot.id'], ),
    sa.PrimaryKeyConstraint('id', 'snapshot_id')
    )
    op.create_table('hackernews',
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('author', sa.String(), nullable=True),
    sa.Column('created_at', sa.String(), nullable=True),
    sa.Column('upvotes', sa.Integer(), nullable=True),
    sa.Column('language', sa.String(), nullable=True),
    sa.Column('sharing_id', sa.String(), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('snapshot_id', sa.String(), nullable=False),
    sa.Column('language_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['language_id'], ['language.code'], ),
    sa.ForeignKeyConstraint(['sharing_id'], ['sharing.id'], ),
    sa.ForeignKeyConstraint(['snapshot_id'], ['snapshot.id'], ),
    sa.PrimaryKeyConstraint('id', 'snapshot_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('hackernews')
    op.drop_table('conversation')
    op.drop_table('sharing')
    op.drop_table('pull_request')
    op.drop_table('issue')
    op.drop_table('discussion')
    op.drop_table('commit')
    op.drop_table('snapshot')
    op.drop_table('language')
    # ### end Alembic commands ###