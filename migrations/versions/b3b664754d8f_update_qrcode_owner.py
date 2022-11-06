"""Update Qrcode owner

Revision ID: b3b664754d8f
Revises: 8b3c20b729a0
Create Date: 2022-11-05 21:36:21.419481

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b3b664754d8f'
down_revision = '8b3c20b729a0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('qrcode')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('qrcode',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('owner', postgresql.ENUM('DEMANDEUR', 'GROUPE', name='choices'), autoincrement=False, nullable=True),
    sa.Column('owner_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('url', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='qrcode_pkey')
    )
    # ### end Alembic commands ###
