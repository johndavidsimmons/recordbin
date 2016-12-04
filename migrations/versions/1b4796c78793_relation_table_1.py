"""relation table 1

Revision ID: 1b4796c78793
Revises: 1eb9a7465f42
Create Date: 2016-12-01 23:17:38.913489

"""

# revision identifiers, used by Alembic.
revision = '1b4796c78793'
down_revision = '1eb9a7465f42'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_titles_name', 'titles')
    op.create_index('ix_titles_name', 'titles', ['name'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_titles_name', 'titles')
    op.create_index('ix_titles_name', 'titles', ['name'], unique=1)
    ### end Alembic commands ###
