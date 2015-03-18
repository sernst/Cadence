from __future__ import print_function, absolute_import, unicode_literals, division

revision = '2f10651e946'
down_revision = '28c48155ac2'

from alembic import op
import sqlalchemy as sqla

def upgrade():
    op.add_column('tracks', sqla.Column('name', sqla.Unicode, default=''))

def downgrade():
    op.drop_column('tracks', sqla.Column('name', sqla.Unicode, default=''))
