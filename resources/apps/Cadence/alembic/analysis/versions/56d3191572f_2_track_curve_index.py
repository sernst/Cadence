"""2: Track curve index

Revision ID: 56d3191572f
Revises: 20addfefc83
Create Date: 2015-05-13 09:35:21.748182

Adds Analysis_Track.curveIndex column
"""

# revision identifiers, used by Alembic.
revision = '56d3191572f'
down_revision = '20addfefc83'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

#_______________________________________________________________________________
def upgrade():
    try:
        op.add_column('tracks', sa.Column('curveIndex', sa.Integer, default=-1))
    except Exception:
        pass

#_______________________________________________________________________________
def downgrade():
    try:
        op.drop_column('tracks', 'curveIndex')
    except Exception:
        pass
