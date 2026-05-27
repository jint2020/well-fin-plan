"""initial schema without physical foreign keys

Revision ID: 202605270001
Revises:
Create Date: 2026-05-27
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202605270001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("refresh_token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])

    op.create_table(
        "user_finance_settings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("salary_min", sa.Numeric(14, 2), nullable=False),
        sa.Column("salary_max", sa.Numeric(14, 2), nullable=False),
        sa.Column("conservative_income_base", sa.Numeric(14, 2), nullable=False),
        sa.Column("necessity_ratio", sa.Numeric(6, 4), nullable=False),
        sa.Column("saving_ratio", sa.Numeric(6, 4), nullable=False),
        sa.Column("flex_ratio", sa.Numeric(6, 4), nullable=False),
        sa.Column("extra_saving_ratio", sa.Numeric(6, 4), nullable=False),
        sa.Column("extra_reserve_ratio", sa.Numeric(6, 4), nullable=False),
        sa.Column("extra_flex_ratio", sa.Numeric(6, 4), nullable=False),
        sa.Column("emergency_months", sa.Integer(), nullable=False),
        sa.Column("monthly_necessity_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("plan_year", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_user_finance_settings_user_id"),
    )
    op.create_index("ix_user_finance_settings_user_id", "user_finance_settings", ["user_id"])

    op.create_table(
        "accounts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("account_type", sa.String(length=80), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uq_accounts_user_id_name"),
    )
    op.create_index("ix_accounts_user_id", "accounts", ["user_id"])

    op.create_table(
        "categories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("transaction_type", sa.String(length=80), nullable=False),
        sa.Column("is_income", sa.Boolean(), nullable=False),
        sa.Column("is_salary", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "transaction_type", "name", name="uq_categories_user_id_type_name"),
    )
    op.create_index("ix_categories_user_id", "categories", ["user_id"])

    op.create_table(
        "transactions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("occurred_on", sa.Date(), nullable=False),
        sa.Column("month", sa.Date(), nullable=False),
        sa.Column("transaction_type", sa.String(length=80), nullable=False),
        sa.Column("counterparty", sa.String(length=255), nullable=True),
        sa.Column("recurrence_type", sa.String(length=80), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"])
    op.create_index("ix_transactions_account_id", "transactions", ["account_id"])
    op.create_index("ix_transactions_category_id", "transactions", ["category_id"])
    op.create_index("ix_transactions_user_month", "transactions", ["user_id", "month"])
    op.create_index("ix_transactions_user_occurred_on", "transactions", ["user_id", "occurred_on"])
    op.create_index("ix_transactions_user_type", "transactions", ["user_id", "transaction_type"])

    op.create_table(
        "emergency_fund_plans",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("month", sa.Date(), nullable=False),
        sa.Column("planned_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("opening_balance", sa.Numeric(14, 2), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "month", name="uq_emergency_fund_plans_user_id_month"),
    )
    op.create_index("ix_emergency_fund_plans_user_id", "emergency_fund_plans", ["user_id"])

    op.create_table(
        "debts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("current_balance", sa.Numeric(14, 2), nullable=False),
        sa.Column("annual_rate", sa.Numeric(8, 6), nullable=False),
        sa.Column("minimum_monthly_payment", sa.Numeric(14, 2), nullable=False),
        sa.Column("extra_monthly_payment", sa.Numeric(14, 2), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uq_debts_user_id_name"),
    )
    op.create_index("ix_debts_user_id", "debts", ["user_id"])

    op.create_table(
        "asset_allocations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("asset_class", sa.String(length=120), nullable=False),
        sa.Column("current_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("target_ratio", sa.Numeric(6, 4), nullable=False),
        sa.Column("risk_level", sa.String(length=40), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "asset_class", name="uq_asset_allocations_user_id_class"),
    )
    op.create_index("ix_asset_allocations_user_id", "asset_allocations", ["user_id"])

    op.create_table(
        "financial_goals",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("goal_type", sa.String(length=80), nullable=False),
        sa.Column("target_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("current_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("monthly_contribution", sa.Numeric(14, 2), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uq_financial_goals_user_id_name"),
    )
    op.create_index("ix_financial_goals_user_id", "financial_goals", ["user_id"])


def downgrade() -> None:
    op.drop_table("financial_goals")
    op.drop_table("asset_allocations")
    op.drop_table("debts")
    op.drop_table("emergency_fund_plans")
    op.drop_table("transactions")
    op.drop_table("categories")
    op.drop_table("accounts")
    op.drop_table("user_finance_settings")
    op.drop_table("auth_sessions")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
