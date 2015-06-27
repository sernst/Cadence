"""3: Remove TrackStores

Revision ID: 2a29feeeda8
Revises: 3d32b4da6ad
Create Date: 2015-06-27 18:37:26.918301

Removes the trackstores table from the database as it is no longer necessary.
"""

# revision identifiers, used by Alembic.
revision = '2a29feeeda8'
down_revision = '3d32b4da6ad'

from alembic import op
import sqlalchemy as sa

def upgrade():
    try:
        op.drop_table('trackStores')
    except Exception:
        pass

def downgrade():
    pass
