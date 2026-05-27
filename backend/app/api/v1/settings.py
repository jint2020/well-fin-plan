from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.finance import SettingsRead, SettingsUpdate
from app.services.finance_service import get_settings, update_settings

router = APIRouter(tags=["settings"])


@router.get("/settings", response_model=SettingsRead)
def read_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_settings(db, current_user.id)


@router.put("/settings", response_model=SettingsRead)
def put_settings(
    payload: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_settings(db, current_user.id, payload)
