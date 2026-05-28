from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.finance import (
    AssetAllocation,
    Category,
    Debt,
    EmergencyFundPlan,
    FinancialGoal,
    Transaction,
    UserFinanceSettings,
)
from app.schemas.finance import (
    AssetAllocationSummaryItemRead,
    AssetAllocationSummaryRead,
    DashboardRead,
    DebtProgressItemRead,
    DebtProgressRead,
    EmergencyFundProgressRead,
    FinancialGoalProgressItemRead,
    FinancialGoalProgressRead,
    IncomePlanRead,
    MonthlyBudgetRead,
    MonthlyExpenseSummaryRead,
    MonthlyIncomeSummaryRead,
)

MONEY = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return Decimal(value or 0).quantize(MONEY, rounding=ROUND_HALF_UP)


def ratio(numerator: Decimal, denominator: Decimal) -> Decimal:
    if denominator == 0:
        return Decimal("0.0000")
    return (numerator / denominator).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


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
    base = Decimal(settings.conservative_income_base)
    budget_income = base
    extra_income = non_salary_income

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
    if actual_total_income == 0:
        status = "待录入"
    elif saving_debt_rate >= Decimal("0.30"):
        status = "优秀"
    else:
        status = "需要关注"

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


def monthly_income_summary(db: Session, user_id: UUID, month: str) -> MonthlyIncomeSummaryRead:
    target_month = parse_month(month)
    salary_income = Decimal("0")
    non_salary_income = Decimal("0")
    by_category: dict[str, Decimal] = {}
    rows = list(
        db.execute(
            select(Transaction, Category)
            .join(Category, Transaction.category_id == Category.id)
            .where(
                Transaction.user_id == user_id,
                Category.user_id == user_id,
                Transaction.month == target_month,
                Category.is_income.is_(True),
            )
            .order_by(Category.sort_order, Transaction.occurred_on, Transaction.id)
        )
    )
    for transaction, category in rows:
        amount = Decimal(transaction.amount)
        if category.is_salary:
            salary_income += amount
        else:
            non_salary_income += amount
        by_category[category.name] = by_category.get(category.name, Decimal("0")) + amount
    total_income = salary_income + non_salary_income
    return MonthlyIncomeSummaryRead(
        month=target_month,
        salary_income=money(salary_income),
        non_salary_income=money(non_salary_income),
        total_income=money(total_income),
        by_category={key: money(value) for key, value in by_category.items()},
    )


def monthly_expense_summary(db: Session, user_id: UUID, month: str) -> MonthlyExpenseSummaryRead:
    target_month = parse_month(month)
    total_expense = Decimal("0")
    by_type: dict[str, Decimal] = {}
    by_category: dict[str, Decimal] = {}
    rows = list(
        db.execute(
            select(Transaction, Category)
            .join(Category, Transaction.category_id == Category.id)
            .where(
                Transaction.user_id == user_id,
                Category.user_id == user_id,
                Transaction.month == target_month,
                Category.is_income.is_(False),
            )
            .order_by(Category.sort_order, Transaction.occurred_on, Transaction.id)
        )
    )
    for transaction, category in rows:
        amount = Decimal(transaction.amount)
        total_expense += amount
        by_type[category.transaction_type] = by_type.get(category.transaction_type, Decimal("0")) + amount
        by_category[category.name] = by_category.get(category.name, Decimal("0")) + amount
    return MonthlyExpenseSummaryRead(
        month=target_month,
        total_expense=money(total_expense),
        by_type={key: money(value) for key, value in by_type.items()},
        by_category={key: money(value) for key, value in by_category.items()},
    )


def emergency_fund_progress(db: Session, user_id: UUID, month: str) -> EmergencyFundProgressRead:
    target_month = parse_month(month)
    settings = _settings(db, user_id)
    target_amount = Decimal(settings.monthly_necessity_amount) * Decimal(settings.emergency_months)
    plan = db.scalar(
        select(EmergencyFundPlan).where(
            EmergencyFundPlan.user_id == user_id,
            EmergencyFundPlan.month == target_month,
        )
    )
    planned_amount = Decimal(plan.planned_amount) if plan is not None else Decimal("0")
    opening_balance = Decimal(plan.opening_balance) if plan is not None else Decimal("0")
    actual_month_deposit = sum(
        (
            Decimal(transaction.amount)
            for transaction in db.scalars(
                select(Transaction)
                .join(Category, Transaction.category_id == Category.id)
                .where(
                    Transaction.user_id == user_id,
                    Category.user_id == user_id,
                    Category.name == "应急金",
                    Transaction.month == target_month,
                )
            )
        ),
        Decimal("0"),
    )
    current_amount = opening_balance + actual_month_deposit
    return EmergencyFundProgressRead(
        month=target_month,
        target_amount=money(target_amount),
        planned_amount=money(planned_amount),
        actual_month_deposit=money(actual_month_deposit),
        current_amount=money(current_amount),
        progress_rate=ratio(current_amount, target_amount),
        remaining_amount=money(max(Decimal("0"), target_amount - current_amount)),
    )


def debt_progress(db: Session, user_id: UUID, month: str) -> DebtProgressRead:
    target_month = parse_month(month)
    debts = list(db.scalars(select(Debt).where(Debt.user_id == user_id).order_by(Debt.name, Debt.id)))
    planned_payment = sum(
        (Decimal(debt.minimum_monthly_payment) + Decimal(debt.extra_monthly_payment) for debt in debts),
        Decimal("0"),
    )
    total_debt = sum((Decimal(debt.current_balance) for debt in debts), Decimal("0"))
    actual_payment = sum(
        (
            Decimal(transaction.amount)
            for transaction in db.scalars(
                select(Transaction)
                .join(Category, Transaction.category_id == Category.id)
                .where(
                    Transaction.user_id == user_id,
                    Category.user_id == user_id,
                    Category.transaction_type == "债务还款",
                    Transaction.month == target_month,
                )
            )
        ),
        Decimal("0"),
    )
    repayment_rate = ratio(actual_payment, planned_payment)
    items = [
        DebtProgressItemRead(
            id=debt.id,
            name=debt.name,
            current_balance=money(Decimal(debt.current_balance)),
            annual_rate=Decimal(debt.annual_rate),
            minimum_monthly_payment=money(Decimal(debt.minimum_monthly_payment)),
            extra_monthly_payment=money(Decimal(debt.extra_monthly_payment)),
            status=debt.status,
            note=debt.note,
            monthly_payment_plan=money(Decimal(debt.minimum_monthly_payment) + Decimal(debt.extra_monthly_payment)),
            monthly_payment_progress_rate=None,
        )
        for debt in debts
    ]
    return DebtProgressRead(
        month=target_month,
        total_debt_balance=money(total_debt),
        planned_monthly_payment=money(planned_payment),
        actual_debt_payment=money(actual_payment),
        repayment_completion_rate=repayment_rate,
        items=items,
    )


def asset_allocation_summary(db: Session, user_id: UUID) -> AssetAllocationSummaryRead:
    assets = list(
        db.scalars(
            select(AssetAllocation)
            .where(AssetAllocation.user_id == user_id)
            .order_by(AssetAllocation.asset_class, AssetAllocation.id)
        )
    )
    total_amount = sum((Decimal(asset.current_amount) for asset in assets), Decimal("0"))
    items = [
        AssetAllocationSummaryItemRead(
            id=asset.id,
            asset_class=asset.asset_class,
            current_amount=money(Decimal(asset.current_amount)),
            target_ratio=Decimal(asset.target_ratio),
            risk_level=asset.risk_level,
            note=asset.note,
            current_ratio=ratio(Decimal(asset.current_amount), total_amount),
            target_amount=money(total_amount * Decimal(asset.target_ratio)),
            gap_amount=money(total_amount * Decimal(asset.target_ratio) - Decimal(asset.current_amount)),
        )
        for asset in assets
    ]
    return AssetAllocationSummaryRead(total_amount=money(total_amount), items=items)


def goal_progress(db: Session, user_id: UUID) -> FinancialGoalProgressRead:
    goals = list(
        db.scalars(
            select(FinancialGoal)
            .where(FinancialGoal.user_id == user_id)
            .order_by(FinancialGoal.name, FinancialGoal.id)
        )
    )
    total_target = sum((Decimal(goal.target_amount) for goal in goals), Decimal("0"))
    total_current = sum((Decimal(goal.current_amount) for goal in goals), Decimal("0"))
    items = [
        FinancialGoalProgressItemRead(
            id=goal.id,
            name=goal.name,
            goal_type=goal.goal_type,
            target_amount=money(Decimal(goal.target_amount)),
            current_amount=money(Decimal(goal.current_amount)),
            monthly_contribution=money(Decimal(goal.monthly_contribution)),
            target_date=goal.target_date,
            status=goal.status,
            progress_rate=ratio(Decimal(goal.current_amount), Decimal(goal.target_amount)),
            remaining_amount=money(max(Decimal("0"), Decimal(goal.target_amount) - Decimal(goal.current_amount))),
        )
        for goal in goals
    ]
    return FinancialGoalProgressRead(
        total_target_amount=money(total_target),
        total_current_amount=money(total_current),
        overall_progress_rate=ratio(total_current, total_target),
        items=items,
    )


def dashboard(db: Session, user_id: UUID, month: str) -> DashboardRead:
    budget = monthly_budget(db, user_id, month)
    emergency_progress = emergency_fund_progress(db, user_id, month)
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
    return DashboardRead(
        monthly_budget=budget,
        income_summary=monthly_income_summary(db, user_id, month),
        expense_summary=monthly_expense_summary(db, user_id, month),
        emergency_fund_progress=emergency_progress,
        debt_progress=debt_progress(db, user_id, month),
        asset_allocation_summary=asset_allocation_summary(db, user_id),
        goal_progress=goal_progress(db, user_id),
        net_assets=money(asset_balance - debt_balance),
        debt_balance=money(debt_balance),
        emergency_fund_balance=emergency_progress.current_amount,
    )


def income_plan(db: Session, user_id: UUID, year: int) -> IncomePlanRead:
    months = [monthly_budget(db, user_id, f"{year}-{month_number:02d}") for month_number in range(1, 13)]
    return IncomePlanRead(year=year, months=months)
