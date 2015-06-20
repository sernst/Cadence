"""3: Stride and Pace Lengths

Revision ID: 335e18a4506
Revises: 56d3191572f
Create Date: 2015-06-20 08:53:32.727550

Adds validation analyzer stride and pace length values.
"""

# revision identifiers, used by Alembic.
revision = '335e18a4506'
down_revision = '56d3191572f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

#___________________________________________________________________________________________________
def upgrade():
    try:
        op.add_column('tracks', sa.Column('strideLength', sa.Float, default=0.0))
        op.add_column('tracks', sa.Column('strideLengthUnc', sa.Float, default=0.0))
        op.add_column('tracks', sa.Column('paceLength', sa.Float, default=0.0))
        op.add_column('tracks', sa.Column('paceLengthUnc', sa.Float, default=0.0))
    except Exception:
        pass

#___________________________________________________________________________________________________
def downgrade():
    try:
        op.drop_column('tracks', 'strideLength')
        op.drop_column('tracks', 'strideLengthUnc')
        op.drop_column('tracks', 'paceLength')
        op.drop_column('tracks', 'paceLengthUnc')
    except Exception:
        pass
