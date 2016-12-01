"""initial record models

Revision ID: 1eb9a7465f42
Revises: 38ce97f49edf
Create Date: 2016-12-01 13:28:10.357154

"""

# revision identifiers, used by Alembic.
revision = '1eb9a7465f42'
down_revision = '38ce97f49edf'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('records')
    op.drop_table('owned')
    op.add_column('titles', sa.Column('notes', sa.String(length=128), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('titles', 'notes')
    op.create_table('owned',
    sa.Column('title_id', sa.INTEGER(), nullable=False),
    sa.Column('owner_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], [u'users_table.id'], ),
    sa.ForeignKeyConstraint(['title_id'], [u'records.id'], ),
    sa.PrimaryKeyConstraint('title_id', 'owner_id')
    )
    op.create_table('records',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.VARCHAR(length=64), nullable=True),
    sa.Column('artist_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], [u'artists.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###
