from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.finance import AssetAllocation, Category, Debt, Transaction, UserFinanceSettings
from app.schemas.finance import DashboardRead, IncomePlanRead, MonthlyBudgetRead

MONEY = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return Decimal(value or 0).quantize(MONEY, rounding=ROUND_HALF_UP)


def parse_month(month: str) -> date:
    try:
        year, month_number = [int(part) for part in month.split("-", 1)]
        return date(year, month_number, 1)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="month must use YYYY-MM format") from exc


def _settings(db: Session, user_id: UUID) -> UserFinanceSettings:
    settings = db.scalar(select(UserFinanceSettings).where(UserFinanceSettings.user_id == user_id))
    if settings is None:
        raise HTTPException(status_code=404, detail="finance settings not found")
    return settings


def monthly_budget(db: Session, user_id: UUID, month: str) -> MonthlyBudgetRead:
    target_month = parse_month(month)
    settings = _settings(db, user_id)
    rows = list(
        db.execute(
            select(Transaction, Category)
            .join(Category, Transaction.category_id == Category.id)
            .where(Transaction.user_id == user_id, Category.user_id == user_id, Transaction.month == target_month)
        )
    )

    salary_income = Decimal("0")
    non_salary_income = Decimal("0")
    actual_necessary = Decimal("0")
    actual_saving = Decimal("0")
    actual_debt = Decimal("0")
    actual_reserve = Decimal("0")
    actual_flex = Decimal("0")

    for transaction, category in rows:
        amount = Decimal(transaction.amount)
        if category.is_income:
            if category.is_salary:
                salary_income += amount
            else:
                non_salary_income += amount
        elif category.transaction_type == "必要支出":
            actual_necessary += amount
        elif category.transaction_type == "储蓄投资":
            actual_saving += amount
        elif category.transaction_type == "债务还款":
            actual_debt += amount
        elif category.transaction_type == "专项准备金":
            actual_reserve += amount
        elif category.transaction_type == "弹性消费":
            actual_flex += amount

    actual_total_income = salary_income + non_salary_income
    budget_income = actual_total_income if actual_total_income > 0 else Decimal(settings.conservative_income_base)
    base = Decimal(settings.conservative_income_base)
    extra_income = max(Decimal("0"), budget_income - base)

    necessary_budget = base * Decimal(settings.necessity_ratio)
    base_saving_budget = base * Decimal(settings.saving_ratio)
    base_flex_budget = base * Decimal(settings.flex_ratio)
    extra_to_saving_debt = extra_income * Decimal(settings.extra_saving_ratio)
    extra_to_reserve = extra_income * Decimal(settings.extra_reserve_ratio)
    extra_to_flex = extra_income * Decimal(settings.extra_flex_ratio)
    recommended_saving_debt = base_saving_budget + extra_to_saving_debt
    recommended_reserve = extra_to_reserve
    recommended_flex = base_flex_budget + extra_to_flex

    total_outflow = actual_necessary + actual_saving + actual_debt + actual_reserve + actual_flex
    surplus = actual_total_income - total_outflow
    saving_debt = actual_saving + actual_debt
    saving_debt_rate = Decimal("0") if actual_total_income == 0 else saving_debt / actual_total_income
    status = "待录入" if actual_total_income == 0 else ("优秀" if saving_debt_rate >= Decimal("0.30") else "需要关注")

    return MonthlyBudgetRead(
        month=target_month,
        salary_income=money(salary_income),
        non_salary_income=money(non_salary_income),
        actual_total_income=money(actual_total_income),
        budget_income=money(budget_income),
        necessary_budget=money(necessary_budget),
        base_saving_budget=money(base_saving_budget),
        base_flex_budget=money(base_flex_budget),
        extra_income=money(extra_income),
        extra_to_saving_debt=money(extra_to_saving_debt),
        extra_to_reserve=money(extra_to_reserve),
        extra_to_flex=money(extra_to_flex),
        recommended_saving_debt=money(recommended_saving_debt),
        recommended_reserve=money(recommended_reserve),
        recommended_flex=money(recommended_flex),
        actual_necessary=money(actual_necessary),
        actual_saving_investment=money(actual_saving),
        actual_flex=money(actual_flex),
        actual_debt_payment=money(actual_debt),
        actual_reserve=money(actual_reserve),
        monthly_surplus=money(surplus),
        saving_debt_rate=saving_debt_rate.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
        status=status,
    )


def dashboard(db: Session, user_id: UUID, month: str) -> DashboardRead:
    budget = monthly_budget(db, user_id, month)
    debt_balance = sum(
        (Decimal(value) for value in db.scalars(select(Debt.current_balance).where(Debt.user_id == user_id))),
        Decimal("0"),
    )
    asset_balance = sum(
        (
            Decimal(value)
            for value in db.scalars(select(AssetAllocation.current_amount).where(AssetAllocation.user_id == user_id))
        ),
        Decimal("0"),
    )
    emergency_balance = sum(
        (
            Decimal(transaction.amount)
            for transaction in db.scalars(
                select(Transaction)
                .join(Category, Transaction.category_id == Category.id)
                .where(
                    Transaction.user_id == user_id,
                    Category.user_id == user_id,
                    Category.name == "应急金",
                )
            )
        ),
        Decimal("0"),
    )
    return DashboardRead(
        monthly_budget=budget,
        net_assets=money(asset_balance - debt_balance),
        debt_balance=money(debt_balance),
        emergency_fund_balance=money(emergency_balance),
    )


def income_plan(db: Session, user_id: UUID, year: int) -> IncomePlanRead:
    months = [monthly_budget(db, user_id, f"{year}-{month_number:02d}") for month_number in range(1, 13)]
    return IncomePlanRead(year=year, months=months)
