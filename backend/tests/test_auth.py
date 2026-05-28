from sqlalchemy import select

from app.core.config import get_settings
from app.models.user import User

from .conftest import auth_headers, register_user


def setup_function():
    get_settings.cache_clear()


def teardown_function():
    get_settings.cache_clear()


def test_register_hashes_password_and_seeds_defaults(client, db_session):
    token = register_user(client, "alice@example.com")

    user = db_session.scalar(select(User).where(User.email == "alice@example.com"))
    assert user is not None
    assert user.password_hash != "SecurePass123!"
    assert user.password_hash.startswith("$2")

    headers = auth_headers(token)
    accounts = client.get("/api/v1/accounts", headers=headers)
    categories = client.get("/api/v1/categories", headers=headers)

    assert accounts.status_code == 200
    assert categories.status_code == 200
    assert any(item["name"] == "工资卡" for item in accounts.json())
    assert any(item["name"] == "工资" and item["is_salary"] for item in categories.json())


def test_login_and_me_return_current_user(client):
    register_user(client, "bob@example.com", "AnotherPass123!")

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "bob@example.com", "password": "AnotherPass123!"},
    )
    assert login.status_code == 200, login.text

    me = client.get("/api/v1/me", headers=auth_headers(login.json()))
    assert me.status_code == 200
    assert me.json()["email"] == "bob@example.com"


def test_finance_endpoint_requires_authentication(client):
    response = client.get("/api/v1/transactions")
    assert response.status_code == 401


def test_auth_rejects_http_when_secure_transport_is_required(client, monkeypatch):
    monkeypatch.setenv("REQUIRE_HTTPS", "true")
    get_settings.cache_clear()

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "SecurePass123!"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "secure transport required"


def test_auth_accepts_trusted_forwarded_https_when_secure_transport_is_required(client, monkeypatch):
    monkeypatch.setenv("REQUIRE_HTTPS", "true")
    monkeypatch.setenv("TRUST_FORWARDED_PROTO", "true")
    get_settings.cache_clear()

    response = client.post(
        "/api/v1/auth/register",
        headers={"X-Forwarded-Proto": "https"},
        json={"email": "secure@example.com", "password": "SecurePass123!", "display_name": "Secure"},
    )

    assert response.status_code == 201, response.text
