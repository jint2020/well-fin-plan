from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.api.deps import get_db
from app.db.base import Base
from app.main import app as fastapi_app


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()


def register_user(client: TestClient, email: str, password: str = "SecurePass123!") -> dict:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "display_name": email.split("@")[0]},
    )
    assert response.status_code == 201, response.text
    return response.json()


def auth_headers(token_response: dict) -> dict[str, str]:
    return {"Authorization": f"Bearer {token_response['access_token']}"}


def get_default_id(client: TestClient, headers: dict[str, str], path: str, name: str) -> str:
    response = client.get(path, headers=headers)
    assert response.status_code == 200, response.text
    for item in response.json():
        if item["name"] == name:
            return item["id"]
    raise AssertionError(f"{name} not found in {path}: {response.json()}")
