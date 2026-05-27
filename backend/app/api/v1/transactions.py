from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.finance import AccountRead, CategoryRead, TransactionCreate, TransactionRead, TransactionUpdate
from app.services.finance_service import (
    create_transaction,
    delete_transaction,
    get_transaction,
    list_accounts,
    list_categories,
    list_transactions,
    update_transaction,
)

router = APIRouter(tags=["finance"])


@router.get("/accounts", response_model=list[AccountRead])
def accounts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_accounts(db, current_user.id)


@router.get("/categories", response_model=list[CategoryRead])
def categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_categories(db, current_user.id)


@router.post("/transactions", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_transaction(db, current_user.id, payload)


@router.get("/transactions", response_model=list[TransactionRead])
def list_(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_transactions(db, current_user.id)


@router.get("/transactions/{transaction_id}", response_model=TransactionRead)
def read(transaction_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_transaction(db, current_user.id, transaction_id)


@router.patch("/transactions/{transaction_id}", response_model=TransactionRead)
def update(
    transaction_id: UUID,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_transaction(db, current_user.id, transaction_id, payload)


@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(transaction_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    delete_transaction(db, current_user.id, transaction_id)
