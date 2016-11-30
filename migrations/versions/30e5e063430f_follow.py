"""follow

Revision ID: 30e5e063430f
Revises: 4f700bb2593d
Create Date: 2016-11-24 18:03:20.633445

"""

# revision identifiers, used by Alembic.
revision = '30e5e063430f'
down_revision = '4f700bb2593d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('follows',
    sa.Column('follower_id', sa.Integer(), nullable=False),
    sa.Column('followed_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['users_table.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['users_table.id'], ),
    sa.PrimaryKeyConstraint('follower_id', 'followed_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('follows')
    ### end Alembic commands ###