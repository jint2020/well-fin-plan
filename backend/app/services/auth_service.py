from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.defaults import seed_user_defaults


def register_user(db: Session, payload: RegisterRequest) -> TokenResponse:
    existing = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing is not None:
        raise ValueError("email_already_registered")
    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
    )
    db.add(user)
    db.flush()
    seed_user_defaults(db, user.id)
    db.commit()
    return TokenResponse(access_token=create_access_token(str(user.id)))


def authenticate_user(db: Session, payload: LoginRequest) -> TokenResponse | None:
    user = db.scalar(select(User).where(User.email == payload.email.lower(), User.is_active.is_(True)))
    if user is None or not verify_password(payload.password, user.password_hash):
        return None
    return TokenResponse(access_token=create_access_token(str(user.id)))
