"""add user_service_id remove service_id user_id in table Appointment

Revision ID: 528f58129840
Revises: 3d5c4d64a722
Create Date: 2026-05-18 18:27:16.357451

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '528f58129840'
down_revision: Union[str, Sequence[str], None] = '3d5c4d64a722'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('appointments') as batch_op:
        batch_op.add_column(sa.Column('user_service_id', sa.Integer(), nullable=False))
        batch_op.drop_column('user_id')
        batch_op.drop_column('service_id')
        batch_op.create_foreign_key(
            'fk_appointments_user_service_id',
            'users',
            ['user_service_id'],
            ['id']
        )


def downgrade() -> None:
    with op.batch_alter_table('appointments') as batch_op:
        batch_op.add_column(sa.Column('service_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.drop_constraint('fk_appointments_user_service_id', type_='foreignkey')
        batch_op.drop_column('user_service_id')
        batch_op.create_foreign_key(
            'fk_appointments_user_id', 'users', ['user_id'], ['id']
        )
        batch_op.create_foreign_key(
            'fk_appointments_service_id', 'services', ['service_id'], ['id']
        )