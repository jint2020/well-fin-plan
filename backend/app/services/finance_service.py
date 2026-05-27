from __future__ import annotations

from datetime import date
from typing import Any, TypeVar
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.finance import (
    Account,
    AssetAllocation,
    Category,
    Debt,
    EmergencyFundPlan,
    FinancialGoal,
    Transaction,
    UserFinanceSettings,
)
from app.schemas.finance import (
    AssetAllocationCreate,
    AssetAllocationUpdate,
    DebtCreate,
    DebtUpdate,
    EmergencyFundPlanUpdate,
    FinancialGoalCreate,
    FinancialGoalUpdate,
    SettingsCreate,
    SettingsUpdate,
    TransactionCreate,
    TransactionUpdate,
)

ModelT = TypeVar("ModelT", Debt, AssetAllocation, FinancialGoal, EmergencyFundPlan)


def month_start(value: date) -> date:
    return date(value.year, value.month, 1)


def list_accounts(db: Session, user_id: UUID) -> list[Account]:
    return list(db.scalars(select(Account).where(Account.user_id == user_id).order_by(Account.name)))


def list_categories(db: Session, user_id: UUID) -> list[Category]:
    return list(db.scalars(select(Category).where(Category.user_id == user_id).order_by(Category.sort_order)))


def get_settings(db: Session, user_id: UUID) -> UserFinanceSettings:
    settings = db.scalar(select(UserFinanceSettings).where(UserFinanceSettings.user_id == user_id))
    if settings is None:
        raise HTTPException(status_code=404, detail="settings not found")
    return settings


def create_settings(db: Session, user_id: UUID, payload: SettingsCreate) -> UserFinanceSettings:
    existing = db.scalar(select(UserFinanceSettings).where(UserFinanceSettings.user_id == user_id))
    if existing is not None:
        raise HTTPException(status_code=409, detail="settings already exist")
    settings = UserFinanceSettings(user_id=user_id, **payload.model_dump())
    db.add(settings)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="settings already exist") from exc
    db.refresh(settings)
    return settings


def update_settings(db: Session, user_id: UUID, payload: SettingsUpdate) -> UserFinanceSettings:
    settings = get_settings(db, user_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(settings, key, value)
    db.commit()
    db.refresh(settings)
    return settings


def delete_settings(db: Session, user_id: UUID) -> None:
    settings = get_settings(db, user_id)
    db.delete(settings)
    db.commit()


def _get_account(db: Session, user_id: UUID, account_id: UUID) -> Account:
    account = db.scalar(select(Account).where(Account.id == account_id, Account.user_id == user_id))
    if account is None:
        raise HTTPException(status_code=422, detail="account_id does not belong to current user")
    return account


def _get_category(db: Session, user_id: UUID, category_id: UUID) -> Category:
    category = db.scalar(select(Category).where(Category.id == category_id, Category.user_id == user_id))
    if category is None:
        raise HTTPException(status_code=422, detail="category_id does not belong to current user")
    return category


def create_transaction(db: Session, user_id: UUID, payload: TransactionCreate) -> Transaction:
    _get_account(db, user_id, payload.account_id)
    category = _get_category(db, user_id, payload.category_id)
    transaction = Transaction(
        user_id=user_id,
        account_id=payload.account_id,
        category_id=payload.category_id,
        occurred_on=payload.occurred_on,
        month=month_start(payload.occurred_on),
        transaction_type=category.transaction_type,
        counterparty=payload.counterparty,
        recurrence_type=payload.recurrence_type,
        description=payload.description,
        amount=payload.amount,
        note=payload.note,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def list_transactions(
    db: Session,
    user_id: UUID,
    *,
    page: int = 1,
    page_size: int = 50,
    month: date | None = None,
    transaction_type: str | None = None,
    category_id: UUID | None = None,
    category: str | None = None,
) -> list[Transaction]:
    statement = select(Transaction).where(Transaction.user_id == user_id)
    if month is not None:
        statement = statement.where(Transaction.month == month)
    if transaction_type is not None:
        statement = statement.where(Transaction.transaction_type == transaction_type)
    if category_id is not None:
        _get_category(db, user_id, category_id)
        statement = statement.where(Transaction.category_id == category_id)
    if category is not None:
        category_statement = select(Category.id).where(Category.user_id == user_id, Category.name == category)
        if transaction_type is not None:
            category_statement = category_statement.where(Category.transaction_type == transaction_type)
        category_ids = list(db.scalars(category_statement))
        if not category_ids:
            return []
        statement = statement.where(Transaction.category_id.in_(category_ids))
    offset = (page - 1) * page_size
    return list(db.scalars(statement.order_by(Transaction.occurred_on, Transaction.id).offset(offset).limit(page_size)))


def get_transaction(db: Session, user_id: UUID, transaction_id: UUID) -> Transaction:
    transaction = db.scalar(select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == user_id))
    if transaction is None:
        raise HTTPException(status_code=404, detail="transaction not found")
    return transaction


def update_transaction(db: Session, user_id: UUID, transaction_id: UUID, payload: TransactionUpdate) -> Transaction:
    transaction = get_transaction(db, user_id, transaction_id)
    data = payload.model_dump(exclude_unset=True)
    if "account_id" in data and data["account_id"] is not None:
        _get_account(db, user_id, data["account_id"])
    if "category_id" in data and data["category_id"] is not None:
        category = _get_category(db, user_id, data["category_id"])
        transaction.transaction_type = category.transaction_type
    for key, value in data.items():
        if key == "occurred_on" and value is not None:
            transaction.month = month_start(value)
        if value is not None:
            setattr(transaction, key, value)
    db.commit()
    db.refresh(transaction)
    return transaction


def delete_transaction(db: Session, user_id: UUID, transaction_id: UUID) -> None:
    transaction = get_transaction(db, user_id, transaction_id)
    db.delete(transaction)
    db.commit()


def create_resource(db: Session, model: type[ModelT], user_id: UUID, payload: Any) -> ModelT:
    resource = model(user_id=user_id, **payload.model_dump())
    db.add(resource)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="resource already exists") from exc
    db.refresh(resource)
    return resource


def _resource_ordering(model: type[ModelT]) -> tuple[Any, ...]:
    if model is EmergencyFundPlan:
        return (EmergencyFundPlan.month, EmergencyFundPlan.id)
    if model is Debt:
        return (Debt.name, Debt.id)
    if model is AssetAllocation:
        return (AssetAllocation.asset_class, AssetAllocation.id)
    if model is FinancialGoal:
        return (FinancialGoal.name, FinancialGoal.id)
    return (model.id,)


def list_resources(
    db: Session,
    model: type[ModelT],
    user_id: UUID,
    *,
    page: int = 1,
    page_size: int = 50,
) -> list[ModelT]:
    offset = (page - 1) * page_size
    statement = select(model).where(model.user_id == user_id).order_by(*_resource_ordering(model))
    return list(db.scalars(statement.offset(offset).limit(page_size)))


def get_resource(db: Session, model: type[ModelT], user_id: UUID, resource_id: UUID, label: str) -> ModelT:
    resource = db.scalar(select(model).where(model.id == resource_id, model.user_id == user_id))
    if resource is None:
        raise HTTPException(status_code=404, detail=f"{label} not found")
    return resource


def update_resource(
    db: Session,
    model: type[ModelT],
    user_id: UUID,
    resource_id: UUID,
    payload: DebtUpdate | AssetAllocationUpdate | FinancialGoalUpdate | EmergencyFundPlanUpdate,
    label: str,
) -> ModelT:
    resource = get_resource(db, model, user_id, resource_id, label)
    for key, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(resource, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"{label} conflicts with an existing resource") from exc
    db.refresh(resource)
    return resource


def delete_resource(db: Session, model: type[ModelT], user_id: UUID, resource_id: UUID, label: str) -> None:
    resource = get_resource(db, model, user_id, resource_id, label)
    db.delete(resource)
    db.commit()
