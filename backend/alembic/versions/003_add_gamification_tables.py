"""add gamification tables

Revision ID: 003_add_gamification
Revises: 002_add_llm_costs_table
Create Date: 2026-02-07

This migration adds gamification tables for:
- Tips: Learning tips for dashboard
- Leaderboard opt-in: Privacy controls for global leaderboard
- Certificates: Course completion certificates

Zero-Backend-LLM: All tables store deterministic data only.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_add_gamification'
down_revision = '002_add_llm_costs_table'
branch_labels = None
depends_on = None


def upgrade():
    # Create tips table
    op.create_table(
        'tips',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('difficulty_level', sa.String(20), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_tips_category', 'tips', ['category'])
    op.create_index('idx_tips_active', 'tips', ['active'])
    op.create_check_constraint('check_tip_active', 'tips', 'active IN (true, false)')

    # Create leaderboard_opt_in table
    op.create_table(
        'leaderboard_opt_in',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('display_name', sa.String(50), nullable=False),
        sa.Column('is_opted_in', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('show_rank', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('show_score', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('show_streak', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_leaderboard_opt_in_user_id', 'leaderboard_opt_in', ['user_id'], unique=True)
    op.create_index('idx_leaderboard_opt_in_opted_in', 'leaderboard_opt_in', ['is_opted_in'])
    op.create_check_constraint('check_opted_in', 'leaderboard_opt_in', 'is_opted_in IN (true, false)')

    # Create certificates table
    op.create_table(
        'certificates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('certificate_id', sa.String(20), nullable=False, unique=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('student_name', sa.String(255), nullable=False),
        sa.Column('completion_percentage', sa.Integer(), nullable=False),
        sa.Column('average_quiz_score', sa.Integer(), nullable=False),
        sa.Column('total_chapters_completed', sa.Integer(), nullable=False),
        sa.Column('total_streak_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('issued_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('verification_count', sa.Integer(), nullable=False, server_default='0'),
    )
    op.create_index('idx_certificates_certificate_id', 'certificates', ['certificate_id'], unique=True)
    op.create_index('idx_certificates_user_id', 'certificates', ['user_id'])
    op.create_check_constraint('check_cert_completion_range', 'certificates', 'completion_percentage >= 0 AND completion_percentage <= 100')
    op.create_check_constraint('check_cert_score_range', 'certificates', 'average_quiz_score >= 0 AND average_quiz_score <= 100')
    op.create_check_constraint('check_cert_chapters_non_negative', 'certificates', 'total_chapters_completed >= 0')


def downgrade():
    # Drop certificates table
    op.drop_table('certificates')

    # Drop leaderboard_opt_in table
    op.drop_table('leaderboard_opt_in')

    # Drop tips table
    op.drop_table('tips')
