"""1: Track Linking

Revision ID: 20addfefc83
Revises: 4b8db18ed61
Create Date: 2015-05-12 22:43:19.574859

Trackway curvature linking column added to the tracks table (nextCurveTrack).
"""

# revision identifiers, used by Alembic.
revision = '20addfefc83'
down_revision = '4b8db18ed61'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sqla


def upgrade():
    try:
        op.add_column('tracks', sqla.Column('nextCurveTrack', sqla.Unicode, default=u''))
    except Exception:
        pass

def downgrade():
    try:
        op.drop_column('tracks', 'nextCurveTrack')
    except Exception:
        pass
