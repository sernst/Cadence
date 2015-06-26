"""2: Tracks Custom Source

Revision ID: 3d32b4da6ad
Revises: 2f10651e946
Create Date: 2015-06-26 11:11:10.039190

Adding source and custom fields to the tracks and trackStores table.
"""

# revision identifiers, used by Alembic.
revision = '3d32b4da6ad'
down_revision = '2f10651e946'

from alembic import op
import sqlalchemy as sa


ENTRY_COLUMNS = [
    ('tracks', sa.Column('source', sa.Unicode, default=u'A16')),
    ('trackStores', sa.Column('source', sa.Unicode, default=u'A16')),

    ('tracks', sa.Column('custom', sa.Boolean, default=False)),
    ('trackStores', sa.Column('custom', sa.Boolean, default=False)) ]

def upgrade():
    for entry in ENTRY_COLUMNS:
        try:
            op.add_column(*entry)
        except Exception as err:
            print('[ERROR]: Adding column %s.%s' % entry)
            print(err)

def downgrade():
    for entry in ENTRY_COLUMNS:
        try:
            op.drop_column(entry[0], entry[1].name)
        except Exception as err:
            print('[ERROR]: Dropping column %s.%s' % (entry[0], entry[1].name))
            print(err)
