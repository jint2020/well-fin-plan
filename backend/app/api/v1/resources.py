from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.finance import AssetAllocation, Debt, EmergencyFundPlan, FinancialGoal
from app.models.user import User
from app.schemas.finance import (
    AssetAllocationCreate,
    AssetAllocationRead,
    AssetAllocationUpdate,
    DebtCreate,
    DebtRead,
    DebtUpdate,
    EmergencyFundPlanCreate,
    EmergencyFundPlanRead,
    EmergencyFundPlanUpdate,
    FinancialGoalCreate,
    FinancialGoalRead,
    FinancialGoalUpdate,
)
from app.services.finance_service import create_resource, delete_resource, get_resource, list_resources, update_resource

router = APIRouter(tags=["finance-resources"])


@router.post("/emergency-fund/plans", response_model=EmergencyFundPlanRead, status_code=status.HTTP_201_CREATED)
def create_emergency_plan(
    payload: EmergencyFundPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_resource(db, EmergencyFundPlan, current_user.id, payload)


@router.get("/emergency-fund/plans", response_model=list[EmergencyFundPlanRead])
def list_emergency_plans(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_resources(db, EmergencyFundPlan, current_user.id)


@router.get("/emergency-fund/plans/{resource_id}", response_model=EmergencyFundPlanRead)
def read_emergency_plan(
    resource_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_resource(db, EmergencyFundPlan, current_user.id, resource_id, "emergency fund plan")


@router.patch("/emergency-fund/plans/{resource_id}", response_model=EmergencyFundPlanRead)
def update_emergency_plan(
    resource_id: UUID,
    payload: EmergencyFundPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_resource(db, EmergencyFundPlan, current_user.id, resource_id, payload, "emergency fund plan")


@router.delete("/emergency-fund/plans/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_emergency_plan(
    resource_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_resource(db, EmergencyFundPlan, current_user.id, resource_id, "emergency fund plan")


@router.post("/debts", response_model=DebtRead, status_code=status.HTTP_201_CREATED)
def create_debt(payload: DebtCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_resource(db, Debt, current_user.id, payload)


@router.get("/debts", response_model=list[DebtRead])
def list_debts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_resources(db, Debt, current_user.id)


@router.get("/debts/{resource_id}", response_model=DebtRead)
def read_debt(resource_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_resource(db, Debt, current_user.id, resource_id, "debt")


@router.patch("/debts/{resource_id}", response_model=DebtRead)
def update_debt(
    resource_id: UUID,
    payload: DebtUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_resource(db, Debt, current_user.id, resource_id, payload, "debt")


@router.delete("/debts/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_debt(resource_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    delete_resource(db, Debt, current_user.id, resource_id, "debt")


@router.post("/asset-allocations", response_model=AssetAllocationRead, status_code=status.HTTP_201_CREATED)
def create_asset(
    payload: AssetAllocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_resource(db, AssetAllocation, current_user.id, payload)


@router.get("/asset-allocations", response_model=list[AssetAllocationRead])
def list_assets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_resources(db, AssetAllocation, current_user.id)


@router.get("/asset-allocations/{resource_id}", response_model=AssetAllocationRead)
def read_asset(resource_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_resource(db, AssetAllocation, current_user.id, resource_id, "asset allocation")


@router.patch("/asset-allocations/{resource_id}", response_model=AssetAllocationRead)
def update_asset(
    resource_id: UUID,
    payload: AssetAllocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_resource(db, AssetAllocation, current_user.id, resource_id, payload, "asset allocation")


@router.delete("/asset-allocations/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(resource_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    delete_resource(db, AssetAllocation, current_user.id, resource_id, "asset allocation")


@router.post("/goals", response_model=FinancialGoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(
    payload: FinancialGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_resource(db, FinancialGoal, current_user.id, payload)


@router.get("/goals", response_model=list[FinancialGoalRead])
def list_goals(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_resources(db, FinancialGoal, current_user.id)


@router.get("/goals/{resource_id}", response_model=FinancialGoalRead)
def read_goal(resource_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_resource(db, FinancialGoal, current_user.id, resource_id, "goal")


@router.patch("/goals/{resource_id}", response_model=FinancialGoalRead)
def update_goal(
    resource_id: UUID,
    payload: FinancialGoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_resource(db, FinancialGoal, current_user.id, resource_id, payload, "goal")


@router.delete("/goals/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(resource_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    delete_resource(db, FinancialGoal, current_user.id, resource_id, "goal")
