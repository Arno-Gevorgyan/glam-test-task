"""002_Instagram model

Revision ID: 8ccbd39d167d
Revises: 86ad584cf7e2
Create Date: 2023-08-10 20:52:01.841262

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8ccbd39d167d'
down_revision = '86ad584cf7e2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('instagram',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('account_username', sa.String(length=100), nullable=True),
    sa.Column('photo_urls', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_instagram_user_id_user'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_instagram')),
    sa.UniqueConstraint('id', name=op.f('uq_instagram_id'))
    )
    op.create_unique_constraint(op.f('uq_user_id'), 'user', ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('uq_user_id'), 'user', type_='unique')
    op.drop_table('instagram')
    # ### end Alembic commands ###
