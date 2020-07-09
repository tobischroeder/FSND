"""empty message

Revision ID: 13bd4d88bcf5
Revises: 21a01ad84a4f
Create Date: 2020-07-07 21:18:49.795856

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '13bd4d88bcf5'
down_revision = '21a01ad84a4f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('name', sa.String(length=120), nullable=True))
    op.alter_column('Show', 'start_time',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.drop_constraint('Show_venue_name_fkey', 'Show', type_='foreignkey')
    op.drop_constraint('Show_artist_image_link_fkey', 'Show', type_='foreignkey')
    op.drop_column('Show', 'artist_image_link')
    op.drop_column('Show', 'venue_name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('venue_name', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('Show', sa.Column('artist_image_link', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.create_foreign_key('Show_artist_image_link_fkey', 'Show', 'Artist', ['artist_image_link'], ['image_link'])
    op.create_foreign_key('Show_venue_name_fkey', 'Show', 'Venue', ['venue_name'], ['name'])
    op.alter_column('Show', 'start_time',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.drop_column('Show', 'name')
    # ### end Alembic commands ###