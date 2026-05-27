from decimal import Decimal

from .conftest import auth_headers, get_default_id, register_user


def _create_transaction(client, headers, amount="7800.00"):
    account_id = get_default_id(client, headers, "/api/v1/accounts", "工资卡")
    category_id = get_default_id(client, headers, "/api/v1/categories", "工资")
    response = client.post(
        "/api/v1/transactions",
        headers=headers,
        json={
            "account_id": account_id,
            "category_id": category_id,
            "occurred_on": "2026-01-05",
            "counterparty": "公司工资",
            "recurrence_type": "浮动",
            "description": "工资到账",
            "amount": amount,
            "note": "isolation test",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_user_cannot_list_read_update_or_delete_another_users_transaction(client):
    alice = auth_headers(register_user(client, "alice@example.com"))
    bob = auth_headers(register_user(client, "bob@example.com"))

    alice_transaction = _create_transaction(client, alice)

    bob_list = client.get("/api/v1/transactions", headers=bob)
    assert bob_list.status_code == 200
    assert bob_list.json() == []

    read = client.get(f"/api/v1/transactions/{alice_transaction['id']}", headers=bob)
    update = client.patch(
        f"/api/v1/transactions/{alice_transaction['id']}",
        headers=bob,
        json={"amount": "1.00"},
    )
    delete = client.delete(f"/api/v1/transactions/{alice_transaction['id']}", headers=bob)

    assert read.status_code == 404
    assert update.status_code == 404
    assert delete.status_code == 404

    alice_read = client.get(f"/api/v1/transactions/{alice_transaction['id']}", headers=alice)
    assert alice_read.status_code == 200
    assert Decimal(alice_read.json()["amount"]) == Decimal("7800.00")


def test_request_user_id_is_rejected_for_finance_create(client):
    alice = auth_headers(register_user(client, "alice@example.com"))
    account_id = get_default_id(client, alice, "/api/v1/accounts", "工资卡")
    category_id = get_default_id(client, alice, "/api/v1/categories", "工资")

    response = client.post(
        "/api/v1/transactions",
        headers=alice,
        json={
            "user_id": "00000000-0000-0000-0000-000000000000",
            "account_id": account_id,
            "category_id": category_id,
            "occurred_on": "2026-01-05",
            "amount": "100.00",
        },
    )

    assert response.status_code == 422


def test_user_cannot_modify_other_users_debt_asset_or_goal(client):
    alice = auth_headers(register_user(client, "alice@example.com"))
    bob = auth_headers(register_user(client, "bob@example.com"))

    debt = client.post(
        "/api/v1/debts",
        headers=alice,
        json={"name": "信用卡分期", "current_balance": "1000", "annual_rate": "0.18"},
    )
    asset = client.post(
        "/api/v1/asset-allocations",
        headers=alice,
        json={"asset_class": "权益基金/股票", "current_amount": "6000", "target_ratio": "0.35"},
    )
    goal = client.post(
        "/api/v1/goals",
        headers=alice,
        json={
            "name": "长期投资账户",
            "goal_type": "长期投资",
            "target_amount": "30000",
            "current_amount": "6000",
        },
    )

    assert debt.status_code == 201, debt.text
    assert asset.status_code == 201, asset.text
    assert goal.status_code == 201, goal.text

    checks = [
        ("/api/v1/debts", debt.json()["id"], {"current_balance": "1"}),
        ("/api/v1/asset-allocations", asset.json()["id"], {"current_amount": "1"}),
        ("/api/v1/goals", goal.json()["id"], {"current_amount": "1"}),
    ]
    for path, resource_id, payload in checks:
        assert client.get(f"{path}/{resource_id}", headers=bob).status_code == 404
        assert client.patch(f"{path}/{resource_id}", headers=bob, json=payload).status_code == 404
        assert client.delete(f"{path}/{resource_id}", headers=bob).status_code == 404


def test_user_cannot_modify_other_users_emergency_fund_plan(client):
    alice = auth_headers(register_user(client, "alice@example.com"))
    bob = auth_headers(register_user(client, "bob@example.com"))

    plan = client.post(
        "/api/v1/emergency-fund/plans",
        headers=alice,
        json={"month": "2026-01-01", "planned_amount": "900", "opening_balance": "0"},
    )
    assert plan.status_code == 201, plan.text
    resource_id = plan.json()["id"]

    assert client.get(f"/api/v1/emergency-fund/plans/{resource_id}", headers=bob).status_code == 404
    assert (
        client.patch(
            f"/api/v1/emergency-fund/plans/{resource_id}",
            headers=bob,
            json={"planned_amount": "1"},
        ).status_code
        == 404
    )
    assert client.delete(f"/api/v1/emergency-fund/plans/{resource_id}", headers=bob).status_code == 404


def test_settings_are_scoped_to_current_user_and_reject_user_id(client):
    alice = auth_headers(register_user(client, "alice@example.com"))
    bob = auth_headers(register_user(client, "bob@example.com"))

    rejected = client.put(
        "/api/v1/settings",
        headers=alice,
        json={"user_id": "00000000-0000-0000-0000-000000000000", "salary_min": "1"},
    )
    assert rejected.status_code == 422

    updated = client.put("/api/v1/settings", headers=alice, json={"salary_min": "6500"})
    assert updated.status_code == 200, updated.text

    bob_settings = client.get("/api/v1/settings", headers=bob)
    assert bob_settings.status_code == 200
    assert Decimal(bob_settings.json()["salary_min"]) == Decimal("7000.00")
