from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, Index, Integer, Numeric, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserFinanceSettings(Base):
    __tablename__ = "user_finance_settings"
    __table_args__ = (
        Index("ix_user_finance_settings_user_id", "user_id"),
        UniqueConstraint("user_id", name="uq_user_finance_settings_user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    salary_min: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("7000.00"))
    salary_max: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("8500.00"))
    conservative_income_base: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("7000.00")
    )
    necessity_ratio: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, default=Decimal("0.5000"))
    saving_ratio: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, default=Decimal("0.3000"))
    flex_ratio: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, default=Decimal("0.2000"))
    extra_saving_ratio: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, default=Decimal("0.7000"))
    extra_reserve_ratio: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, default=Decimal("0.2000"))
    extra_flex_ratio: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, default=Decimal("0.1000"))
    emergency_months: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    monthly_necessity_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("4000.00")
    )
    plan_year: Mapped[int] = mapped_column(Integer, nullable=False, default=2026)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        Index("ix_accounts_user_id", "user_id"),
        UniqueConstraint("user_id", "name", name="uq_accounts_user_id_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    account_type: Mapped[str] = mapped_column(String(80), nullable=False, default="现金账户")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        Index("ix_categories_user_id", "user_id"),
        UniqueConstraint("user_id", "transaction_type", "name", name="uq_categories_user_id_type_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(80), nullable=False)
    is_income: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_salary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        Index("ix_transactions_user_id", "user_id"),
        Index("ix_transactions_account_id", "account_id"),
        Index("ix_transactions_category_id", "category_id"),
        Index("ix_transactions_user_month", "user_id", "month"),
        Index("ix_transactions_user_occurred_on", "user_id", "occurred_on"),
        Index("ix_transactions_user_type", "user_id", "transaction_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    account_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    occurred_on: Mapped[date] = mapped_column(Date, nullable=False)
    month: Mapped[date] = mapped_column(Date, nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(80), nullable=False)
    counterparty: Mapped[str | None] = mapped_column(String(255))
    recurrence_type: Mapped[str | None] = mapped_column(String(80))
    description: Mapped[str | None] = mapped_column(String(255))
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )


class EmergencyFundPlan(Base):
    __tablename__ = "emergency_fund_plans"
    __table_args__ = (
        Index("ix_emergency_fund_plans_user_id", "user_id"),
        UniqueConstraint("user_id", "month", name="uq_emergency_fund_plans_user_id_month"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    month: Mapped[date] = mapped_column(Date, nullable=False)
    planned_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    note: Mapped[str | None] = mapped_column(Text)


class Debt(Base):
    __tablename__ = "debts"
    __table_args__ = (
        Index("ix_debts_user_id", "user_id"),
        UniqueConstraint("user_id", "name", name="uq_debts_user_id_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    current_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    annual_rate: Mapped[Decimal] = mapped_column(Numeric(8, 6), nullable=False)
    minimum_monthly_payment: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0.00")
    )
    extra_monthly_payment: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")
    note: Mapped[str | None] = mapped_column(Text)


class AssetAllocation(Base):
    __tablename__ = "asset_allocations"
    __table_args__ = (
        Index("ix_asset_allocations_user_id", "user_id"),
        UniqueConstraint("user_id", "asset_class", name="uq_asset_allocations_user_id_class"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    asset_class: Mapped[str] = mapped_column(String(120), nullable=False)
    current_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    target_ratio: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    risk_level: Mapped[str | None] = mapped_column(String(40))
    note: Mapped[str | None] = mapped_column(Text)


class FinancialGoal(Base):
    __tablename__ = "financial_goals"
    __table_args__ = (
        Index("ix_financial_goals_user_id", "user_id"),
        UniqueConstraint("user_id", "name", name="uq_financial_goals_user_id_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    goal_type: Mapped[str] = mapped_column(String(80), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    current_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    monthly_contribution: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    target_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")
