"""glucose

Revision ID: afe97a63ab52
Revises: 
Create Date: 2024-11-22 08:59:42.727993

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afe97a63ab52'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bloom_users',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_superuser', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bloom_users_email'), 'bloom_users', ['email'], unique=True)
    op.create_index(op.f('ix_bloom_users_id'), 'bloom_users', ['id'], unique=False)
    op.create_table('bloom_checkups',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('pregnancy_week', sa.Integer(), nullable=True),
    sa.Column('checkup_date', sa.Date(), nullable=False),
    sa.Column('doctor_id', sa.String(length=36), nullable=True),
    sa.Column('next_appointment', sa.Date(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['bloom_users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bloom_checkups_id'), 'bloom_checkups', ['id'], unique=False)
    op.create_table('bloom_glucose',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('glucose_value', sa.Float(), nullable=False),
    sa.Column('glucose_date', sa.Date(), nullable=False),
    sa.Column('measurement_type', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['bloom_users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bloom_glucose_id'), 'bloom_glucose', ['id'], unique=False)
    op.create_table('bloom_patients',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('date_of_birth', sa.Date(), nullable=False),
    sa.Column('blood_type', sa.String(length=10), nullable=True),
    sa.Column('rh_factor', sa.String(length=1), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('emergency_contact', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['bloom_users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bloom_patients_id'), 'bloom_patients', ['id'], unique=False)
    op.create_table('bloom_lab_results',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('checkup_id', sa.BigInteger(), nullable=False),
    sa.Column('hemoglobin', sa.Numeric(precision=4, scale=1), nullable=True),
    sa.Column('blood_glucose', sa.Numeric(precision=4, scale=1), nullable=True),
    sa.Column('hbsag', sa.String(length=10), nullable=True),
    sa.Column('hiv', sa.String(length=10), nullable=True),
    sa.Column('syphilis', sa.String(length=10), nullable=True),
    sa.Column('tsh', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('urine_protein', sa.String(length=10), nullable=True),
    sa.Column('urine_glucose', sa.String(length=10), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['checkup_id'], ['bloom_checkups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bloom_lab_results_id'), 'bloom_lab_results', ['id'], unique=False)
    op.create_table('bloom_prenatal_screenings',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('checkup_id', sa.BigInteger(), nullable=False),
    sa.Column('screening_type', sa.String(length=50), nullable=True),
    sa.Column('screening_date', sa.Date(), nullable=True),
    sa.Column('result', sa.Text(), nullable=True),
    sa.Column('risk_assessment', sa.String(length=50), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['checkup_id'], ['bloom_checkups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bloom_prenatal_screenings_id'), 'bloom_prenatal_screenings', ['id'], unique=False)
    op.create_table('bloom_recommendations',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('checkup_id', sa.BigInteger(), nullable=False),
    sa.Column('category', sa.String(length=50), nullable=True),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('priority', sa.String(length=20), nullable=True),
    sa.Column('valid_until', sa.Date(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['checkup_id'], ['bloom_checkups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bloom_recommendations_id'), 'bloom_recommendations', ['id'], unique=False)
    op.create_table('bloom_ultrasounds',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('checkup_id', sa.BigInteger(), nullable=False),
    sa.Column('head_circumference', sa.Numeric(precision=4, scale=1), nullable=True),
    sa.Column('abdominal_circumference', sa.Numeric(precision=4, scale=1), nullable=True),
    sa.Column('femur_length', sa.Numeric(precision=4, scale=1), nullable=True),
    sa.Column('estimated_weight', sa.Numeric(precision=6, scale=2), nullable=True),
    sa.Column('fetal_position', sa.String(length=20), nullable=True),
    sa.Column('amniotic_fluid_index', sa.Numeric(precision=4, scale=1), nullable=True),
    sa.Column('placenta_position', sa.String(length=20), nullable=True),
    sa.Column('placenta_grade', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['checkup_id'], ['bloom_checkups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bloom_ultrasounds_id'), 'bloom_ultrasounds', ['id'], unique=False)
    op.create_table('bloom_vital_signs',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('checkup_id', sa.BigInteger(), nullable=False),
    sa.Column('weight', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('weight_gain', sa.Numeric(precision=4, scale=2), nullable=True),
    sa.Column('blood_pressure_sys', sa.Integer(), nullable=True),
    sa.Column('blood_pressure_dia', sa.Integer(), nullable=True),
    sa.Column('temperature', sa.Numeric(precision=3, scale=1), nullable=True),
    sa.Column('fundal_height', sa.Numeric(precision=4, scale=1), nullable=True),
    sa.Column('fetal_heart_rate', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['checkup_id'], ['bloom_checkups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bloom_vital_signs_id'), 'bloom_vital_signs', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_bloom_vital_signs_id'), table_name='bloom_vital_signs')
    op.drop_table('bloom_vital_signs')
    op.drop_index(op.f('ix_bloom_ultrasounds_id'), table_name='bloom_ultrasounds')
    op.drop_table('bloom_ultrasounds')
    op.drop_index(op.f('ix_bloom_recommendations_id'), table_name='bloom_recommendations')
    op.drop_table('bloom_recommendations')
    op.drop_index(op.f('ix_bloom_prenatal_screenings_id'), table_name='bloom_prenatal_screenings')
    op.drop_table('bloom_prenatal_screenings')
    op.drop_index(op.f('ix_bloom_lab_results_id'), table_name='bloom_lab_results')
    op.drop_table('bloom_lab_results')
    op.drop_index(op.f('ix_bloom_patients_id'), table_name='bloom_patients')
    op.drop_table('bloom_patients')
    op.drop_index(op.f('ix_bloom_glucose_id'), table_name='bloom_glucose')
    op.drop_table('bloom_glucose')
    op.drop_index(op.f('ix_bloom_checkups_id'), table_name='bloom_checkups')
    op.drop_table('bloom_checkups')
    op.drop_index(op.f('ix_bloom_users_id'), table_name='bloom_users')
    op.drop_index(op.f('ix_bloom_users_email'), table_name='bloom_users')
    op.drop_table('bloom_users')
    # ### end Alembic commands ###
