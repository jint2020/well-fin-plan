from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.finance import SettingsCreate, SettingsRead, SettingsUpdate
from app.services.finance_service import create_settings, delete_settings, get_settings, update_settings

router = APIRouter(tags=["settings"])


@router.get("/settings", response_model=SettingsRead)
def read_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_settings(db, current_user.id)


@router.post("/settings", response_model=SettingsRead, status_code=status.HTTP_201_CREATED)
def post_settings(
    payload: SettingsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_settings(db, current_user.id, payload)


@router.put("/settings", response_model=SettingsRead)
def put_settings(
    payload: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_settings(db, current_user.id, payload)


@router.patch("/settings", response_model=SettingsRead)
def patch_settings(
    payload: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_settings(db, current_user.id, payload)


@router.delete("/settings", status_code=status.HTTP_204_NO_CONTENT)
def remove_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    delete_settings(db, current_user.id)
