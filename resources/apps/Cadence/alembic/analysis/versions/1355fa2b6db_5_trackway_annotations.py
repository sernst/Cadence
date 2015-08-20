"""5: Trackway annotations

Revision ID: 1355fa2b6db
Revises: 52ff2449e19
Create Date: 2015-08-19 15:23:01.906026

Adds trackway index and name to the analysis tracks table for per trackway analysis under non-orm circumstances.
"""

from __future__ import \
    print_function, absolute_import, \
    unicode_literals, division

# revision identifiers, used by Alembic.
revision = '1355fa2b6db'
down_revision = '52ff2449e19'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

ENTRIES = [
    ('tracks', 'trackwayIndex', sa.Integer, 0),
    ('tracks', 'trackwayName', sa.Unicode, '') ]

#_______________________________________________________________________________
def upgrade():
    for entry in ENTRIES:
        try:
            op.add_column(
                entry[0],
                sa.Column(entry[1], entry[2], default=entry[3]))
        except Exception as err:
            print('[ERROR]: Adding column %s.%s' % entry[:2])
            print(err)

#_______________________________________________________________________________
def downgrade():
    for entry in ENTRIES:
        try:
            op.drop_column(entry[0], entry[1])
        except Exception as err:
            print('[ERROR]: Dropping column %s.%s' % entry[:2])
            print(err)
