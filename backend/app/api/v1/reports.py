from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.finance import (
    DashboardRead,
    IncomePlanRead,
    MonthlyBudgetRead,
    MonthlyExpenseSummaryRead,
    MonthlyIncomeSummaryRead,
)
from app.services.report_service import (
    dashboard,
    income_plan,
    monthly_budget,
    monthly_expense_summary,
    monthly_income_summary,
)

router = APIRouter(tags=["reports"])


@router.get("/reports/monthly-budget", response_model=MonthlyBudgetRead)
def monthly_budget_report(
    month: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return monthly_budget(db, current_user.id, month)


@router.get("/reports/monthly-income", response_model=MonthlyIncomeSummaryRead)
def monthly_income_report(
    month: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return monthly_income_summary(db, current_user.id, month)


@router.get("/reports/monthly-expenses", response_model=MonthlyExpenseSummaryRead)
def monthly_expense_report(
    month: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return monthly_expense_summary(db, current_user.id, month)


@router.get("/dashboard/monthly", response_model=DashboardRead)
def monthly_dashboard(
    month: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return dashboard(db, current_user.id, month)


@router.get("/reports/income-plan", response_model=IncomePlanRead)
def income_plan_report(
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return income_plan(db, current_user.id, year)
