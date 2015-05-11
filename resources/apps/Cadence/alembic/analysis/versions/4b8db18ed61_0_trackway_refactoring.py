"""0: Trackway refactoring

Revision ID: 4b8db18ed61
Revises:
Create Date: 2015-05-11 11:37:23.700746

Updates the trackway table to rename referenceSeries property the curveSeries property.
"""

# revision identifiers, used by Alembic.
revision = '4b8db18ed61'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    pass

def downgrade():
    pass
