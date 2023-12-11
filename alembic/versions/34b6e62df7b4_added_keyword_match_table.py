"""Added keyword match table

Revision ID: 34b6e62df7b4
Revises: d85942c0f15f
Create Date: 2023-12-10 23:26:50.484049

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34b6e62df7b4'
down_revision: Union[str, None] = 'd85942c0f15f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('keywordmatch',
    sa.Column('keyword', sa.String(), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('snapshot_id', sa.String(), nullable=False),
    sa.Column('column_name', sa.String(), nullable=False),
    sa.Column('table', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['snapshot_id'], ['snapshot.id'], ),
    sa.PrimaryKeyConstraint('id', 'snapshot_id', 'keyword', 'column_name')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('keywordmatch')
    # ### end Alembic commands ###