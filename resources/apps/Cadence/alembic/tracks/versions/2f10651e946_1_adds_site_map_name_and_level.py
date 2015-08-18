"""1: Adds site map name and level

Revision ID: 2f10651e946
Revises: 28c48155ac2
Create Date: 2014-11-27 20:04:38.325891

sitemaps table gets explicit name and level columns to support searching on those attributes instead of them residing within the filename property.
"""

# revision identifiers, used by Alembic.
revision = '2f10651e946'
down_revision = '28c48155ac2'

from alembic import op
import sqlalchemy as sqla

#_______________________________________________________________________________
def upgrade():
    op.add_column('sitemaps', sqla.Column('name', sqla.Unicode, default=''))
    op.add_column('sitemaps', sqla.Column('level', sqla.Unicode, default=''))

#_______________________________________________________________________________
def downgrade():
    op.drop_column('sitemaps', sqla.Column('name', sqla.Unicode, default=''))
    op.drop_column('sitemaps', sqla.Column('level', sqla.Unicode, default=''))
