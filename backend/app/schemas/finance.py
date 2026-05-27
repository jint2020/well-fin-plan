from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StrictFinanceModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    account_type: str
    is_active: bool


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    transaction_type: str
    is_income: bool
    is_salary: bool
    sort_order: int


class SettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    salary_min: Decimal
    salary_max: Decimal
    conservative_income_base: Decimal
    necessity_ratio: Decimal
    saving_ratio: Decimal
    flex_ratio: Decimal
    extra_saving_ratio: Decimal
    extra_reserve_ratio: Decimal
    extra_flex_ratio: Decimal
    emergency_months: int
    monthly_necessity_amount: Decimal
    plan_year: int


class SettingsUpdate(StrictFinanceModel):
    salary_min: Decimal | None = Field(default=None, ge=0)
    salary_max: Decimal | None = Field(default=None, ge=0)
    conservative_income_base: Decimal | None = Field(default=None, ge=0)
    necessity_ratio: Decimal | None = Field(default=None, ge=0)
    saving_ratio: Decimal | None = Field(default=None, ge=0)
    flex_ratio: Decimal | None = Field(default=None, ge=0)
    extra_saving_ratio: Decimal | None = Field(default=None, ge=0)
    extra_reserve_ratio: Decimal | None = Field(default=None, ge=0)
    extra_flex_ratio: Decimal | None = Field(default=None, ge=0)
    emergency_months: int | None = Field(default=None, ge=1)
    monthly_necessity_amount: Decimal | None = Field(default=None, ge=0)
    plan_year: int | None = Field(default=None, ge=2000)


class TransactionCreate(StrictFinanceModel):
    account_id: UUID
    category_id: UUID
    occurred_on: date
    counterparty: str | None = Field(default=None, max_length=255)
    recurrence_type: str | None = Field(default=None, max_length=80)
    description: str | None = Field(default=None, max_length=255)
    amount: Decimal = Field(gt=0)
    note: str | None = None


class TransactionUpdate(StrictFinanceModel):
    account_id: UUID | None = None
    category_id: UUID | None = None
    occurred_on: date | None = None
    counterparty: str | None = Field(default=None, max_length=255)
    recurrence_type: str | None = Field(default=None, max_length=80)
    description: str | None = Field(default=None, max_length=255)
    amount: Decimal | None = Field(default=None, gt=0)
    note: str | None = None


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    account_id: UUID
    category_id: UUID
    occurred_on: date
    month: date
    transaction_type: str
    counterparty: str | None
    recurrence_type: str | None
    description: str | None
    amount: Decimal
    note: str | None


class DebtCreate(StrictFinanceModel):
    name: str
    current_balance: Decimal = Field(ge=0)
    annual_rate: Decimal = Field(ge=0)
    minimum_monthly_payment: Decimal = Field(default=Decimal("0"), ge=0)
    extra_monthly_payment: Decimal = Field(default=Decimal("0"), ge=0)
    status: str = "active"
    note: str | None = None


class EmergencyFundPlanCreate(StrictFinanceModel):
    month: date
    planned_amount: Decimal = Field(ge=0)
    opening_balance: Decimal = Field(default=Decimal("0"), ge=0)
    note: str | None = None


class EmergencyFundPlanUpdate(StrictFinanceModel):
    month: date | None = None
    planned_amount: Decimal | None = Field(default=None, ge=0)
    opening_balance: Decimal | None = Field(default=None, ge=0)
    note: str | None = None


class EmergencyFundPlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    month: date
    planned_amount: Decimal
    opening_balance: Decimal
    note: str | None


class DebtUpdate(StrictFinanceModel):
    name: str | None = None
    current_balance: Decimal | None = Field(default=None, ge=0)
    annual_rate: Decimal | None = Field(default=None, ge=0)
    minimum_monthly_payment: Decimal | None = Field(default=None, ge=0)
    extra_monthly_payment: Decimal | None = Field(default=None, ge=0)
    status: str | None = None
    note: str | None = None


class DebtRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    current_balance: Decimal
    annual_rate: Decimal
    minimum_monthly_payment: Decimal
    extra_monthly_payment: Decimal
    status: str
    note: str | None


class AssetAllocationCreate(StrictFinanceModel):
    asset_class: str
    current_amount: Decimal = Field(ge=0)
    target_ratio: Decimal = Field(ge=0)
    risk_level: str | None = None
    note: str | None = None


class AssetAllocationUpdate(StrictFinanceModel):
    asset_class: str | None = None
    current_amount: Decimal | None = Field(default=None, ge=0)
    target_ratio: Decimal | None = Field(default=None, ge=0)
    risk_level: str | None = None
    note: str | None = None


class AssetAllocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    asset_class: str
    current_amount: Decimal
    target_ratio: Decimal
    risk_level: str | None
    note: str | None


class FinancialGoalCreate(StrictFinanceModel):
    name: str
    goal_type: str
    target_amount: Decimal = Field(gt=0)
    current_amount: Decimal = Field(default=Decimal("0"), ge=0)
    monthly_contribution: Decimal = Field(default=Decimal("0"), ge=0)
    target_date: date | None = None
    status: str = "active"


class FinancialGoalUpdate(StrictFinanceModel):
    name: str | None = None
    goal_type: str | None = None
    target_amount: Decimal | None = Field(default=None, gt=0)
    current_amount: Decimal | None = Field(default=None, ge=0)
    monthly_contribution: Decimal | None = Field(default=None, ge=0)
    target_date: date | None = None
    status: str | None = None


class FinancialGoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    goal_type: str
    target_amount: Decimal
    current_amount: Decimal
    monthly_contribution: Decimal
    target_date: date | None
    status: str


class MonthlyBudgetRead(BaseModel):
    month: date
    salary_income: Decimal
    non_salary_income: Decimal
    actual_total_income: Decimal
    budget_income: Decimal
    necessary_budget: Decimal
    base_saving_budget: Decimal
    base_flex_budget: Decimal
    extra_income: Decimal
    extra_to_saving_debt: Decimal
    extra_to_reserve: Decimal
    extra_to_flex: Decimal
    recommended_saving_debt: Decimal
    recommended_reserve: Decimal
    recommended_flex: Decimal
    actual_necessary: Decimal
    actual_saving_investment: Decimal
    actual_flex: Decimal
    actual_debt_payment: Decimal
    actual_reserve: Decimal
    monthly_surplus: Decimal
    saving_debt_rate: Decimal
    status: str


class IncomePlanRead(BaseModel):
    year: int
    months: list[MonthlyBudgetRead]


class DashboardRead(BaseModel):
    monthly_budget: MonthlyBudgetRead
    net_assets: Decimal
    debt_balance: Decimal
    emergency_fund_balance: Decimal
