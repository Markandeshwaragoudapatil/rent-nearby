"""Add owner applications for reviewed owner onboarding.

Revision ID: 20261127_0002
Revises: 20261127_0001
"""
from alembic import op
import sqlalchemy as sa

revision = "20261127_0002"
down_revision = "20261127_0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "owner_applications",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("business_name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("contact_phone", sa.String(20), nullable=False),
        sa.Column("city", sa.String(100), nullable=False, server_default="Bengaluru"),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("decision_note", sa.String(500)),
        sa.Column("reviewed_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('PENDING','APPROVED','REJECTED')", name="ck_owner_application_status"),
    )
    op.create_index("ix_owner_applications_user_id", "owner_applications", ["user_id"], unique=True)


def downgrade():
    op.drop_index("ix_owner_applications_user_id", table_name="owner_applications")
    op.drop_table("owner_applications")
