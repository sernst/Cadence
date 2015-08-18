"""4: Adds track heading and simple gauge

Revision ID: 52ff2449e19
Revises: 335e18a4506
Create Date: 2015-06-20 16:15:44.521476

Adds heading (degrees) and simple gauge (projection length) properties with uncertainty.
"""

# revision identifiers, used by Alembic.
revision = '52ff2449e19'
down_revision = '335e18a4506'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

#_______________________________________________________________________________
def upgrade():
    entries = [
        ('tracks', sa.Column('headingAngle', sa.Float, default=0.0)),
        ('tracks', sa.Column('headingAngleUnc', sa.Float, default=0.0)),
        ('tracks', sa.Column('simpleGauge', sa.Float, default=0.0)),
        ('tracks', sa.Column('simpleGaugeUnc', sa.Float, default=0.0)),
        ('trackways', sa.Column('simpleGauge', sa.Float, default=0.0)),
        ('trackways', sa.Column('simpleGaugeUnc', sa.Float, default=0.0)) ]

    for entry in entries:
        try:
            op.add_column(*entry)
        except Exception as err:
            print('[ERROR]: Adding column %s.%s' % entry)
            print(err)

#_______________________________________________________________________________
def downgrade():
    entries = [
        ('tracks', 'headingAngle'),
        ('tracks', 'headingAngleUnc'),
        ('tracks', 'simpleGauge'),
        ('tracks', 'simpleGaugeUnc'),
        ('trackways', 'simpleGauge'),
        ('trackways', 'simpleGaugeUnc') ]

    for entry in entries:
        try:
            op.drop_column(*entry)
        except Exception as err:
            print('[ERROR]: Dropping column %s.%s' % entry)
            print(err)
