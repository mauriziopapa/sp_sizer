"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(100), unique=True, nullable=False),
        sa.Column("email", sa.String(200), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(300), nullable=False),
        sa.Column("role", sa.String(50), server_default="ADMIN"),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "sizer_sections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("owner_role", sa.String(100), nullable=True),
        sa.Column("display_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("max_score_theoretical", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "sizer_factors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("section_id", sa.Integer(), sa.ForeignKey("sizer_sections.id"), nullable=False),
        sa.Column("code", sa.String(20), unique=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("weight", sa.Integer(), nullable=False),
        sa.Column("min_score", sa.Integer(), server_default="1", nullable=False),
        sa.Column("max_score", sa.Integer(), server_default="5", nullable=False),
        sa.Column("score_labels", postgresql.JSONB(), nullable=True),
        sa.Column("sub_area", sa.String(100), nullable=True),
        sa.Column("owner_role", sa.String(50), nullable=True),
        sa.Column("display_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("weight >= 1 AND weight <= 10", name="ck_factor_weight"),
    )

    op.create_table(
        "score_ranges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("size_code", sa.String(50), unique=True, nullable=False),
        sa.Column("size_label", sa.String(200), nullable=False),
        sa.Column("min_score", sa.Integer(), nullable=False),
        sa.Column("max_score", sa.Integer(), nullable=False),
        sa.Column("color", sa.String(20), nullable=True),
        sa.Column("emoji", sa.String(10), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("display_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "governance_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("element", sa.String(200), nullable=False),
        sa.Column("score_range_id", sa.Integer(), sa.ForeignKey("score_ranges.id"), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("display_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "risk_flags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("label", sa.String(300), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("condition_logic", postgresql.JSONB(), nullable=True),
        sa.Column("severity", sa.String(20), server_default="WARNING"),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("display_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "project_sizings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_name", sa.String(300), nullable=False),
        sa.Column("client_name", sa.String(300), nullable=True),
        sa.Column("compiled_by", sa.String(200), nullable=True),
        sa.Column("validated_by", sa.String(200), nullable=True),
        sa.Column("sizing_date", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("responses", postgresql.JSONB(), nullable=False),
        sa.Column("notes", postgresql.JSONB(), nullable=True),
        sa.Column("section_scores", postgresql.JSONB(), nullable=False),
        sa.Column("total_raw_score", sa.Integer(), nullable=False),
        sa.Column("total_max_score", sa.Integer(), nullable=False),
        sa.Column("normalized_score", sa.Integer(), nullable=False),
        sa.Column("resulting_size", sa.String(50), nullable=False),
        sa.Column("completeness", postgresql.JSONB(), nullable=False),
        sa.Column("triggered_risk_flags", postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.String(50), server_default="DRAFT"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("project_sizings")
    op.drop_table("risk_flags")
    op.drop_table("governance_rules")
    op.drop_table("score_ranges")
    op.drop_table("sizer_factors")
    op.drop_table("sizer_sections")
    op.drop_table("users")
