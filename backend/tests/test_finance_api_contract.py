from decimal import Decimal

from .conftest import auth_headers, get_default_id, register_user


def _post_transaction(client, headers, account_name, category_name, occurred_on, amount):
    account_id = get_default_id(client, headers, "/api/v1/accounts", account_name)
    category_id = get_default_id(client, headers, "/api/v1/categories", category_name)
    response = client.post(
        "/api/v1/transactions",
        headers=headers,
        json={
            "account_id": account_id,
            "category_id": category_id,
            "occurred_on": occurred_on,
            "amount": amount,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_settings_support_create_read_update_delete_without_request_user_id(client):
    headers = auth_headers(register_user(client, "settings@example.com"))

    rejected = client.post(
        "/api/v1/settings",
        headers=headers,
        json={"user_id": "00000000-0000-0000-0000-000000000000", "salary_min": "1"},
    )
    assert rejected.status_code == 422

    deleted = client.delete("/api/v1/settings", headers=headers)
    assert deleted.status_code == 204, deleted.text
    assert client.get("/api/v1/settings", headers=headers).status_code == 404

    created = client.post(
        "/api/v1/settings",
        headers=headers,
        json={
            "salary_min": "6500",
            "salary_max": "9000",
            "conservative_income_base": "6500",
            "monthly_necessity_amount": "3600",
        },
    )
    assert created.status_code == 201, created.text
    assert Decimal(created.json()["salary_min"]) == Decimal("6500.00")

    duplicate = client.post("/api/v1/settings", headers=headers, json={})
    assert duplicate.status_code == 409

    updated = client.patch("/api/v1/settings", headers=headers, json={"salary_min": "6800"})
    assert updated.status_code == 200, updated.text
    assert Decimal(updated.json()["salary_min"]) == Decimal("6800.00")


def test_transactions_support_month_type_category_filters_and_pagination(client):
    headers = auth_headers(register_user(client, "filters@example.com"))
    salary = _post_transaction(client, headers, "工资卡", "工资", "2026-01-05", "7000")
    food = _post_transaction(client, headers, "生活账户", "餐饮", "2026-01-06", "800")
    _post_transaction(client, headers, "工资卡", "副业收入", "2026-02-05", "1200")

    january_income = client.get("/api/v1/transactions?month=2026-01&type=收入", headers=headers)
    assert january_income.status_code == 200, january_income.text
    assert [item["id"] for item in january_income.json()] == [salary["id"]]

    food_only = client.get(f"/api/v1/transactions?category_id={food['category_id']}", headers=headers)
    assert food_only.status_code == 200, food_only.text
    assert [item["id"] for item in food_only.json()] == [food["id"]]

    first_page = client.get("/api/v1/transactions?page=1&page_size=2", headers=headers)
    second_page = client.get("/api/v1/transactions?page=2&page_size=2", headers=headers)
    assert first_page.status_code == 200, first_page.text
    assert second_page.status_code == 200, second_page.text
    assert len(first_page.json()) == 2
    assert len(second_page.json()) == 1

    invalid_month = client.get("/api/v1/transactions?month=2026/01", headers=headers)
    assert invalid_month.status_code == 422


def test_monthly_income_and_expense_summaries_are_scoped_to_current_user(client):
    alice = auth_headers(register_user(client, "alice-summary@example.com"))
    bob = auth_headers(register_user(client, "bob-summary@example.com"))

    _post_transaction(client, alice, "工资卡", "工资", "2026-01-05", "7000")
    _post_transaction(client, alice, "工资卡", "副业收入", "2026-01-08", "1000")
    _post_transaction(client, alice, "生活账户", "餐饮", "2026-01-10", "900")
    _post_transaction(client, alice, "快乐消费账户", "娱乐", "2026-01-11", "100")
    _post_transaction(client, bob, "工资卡", "工资", "2026-01-05", "99999")

    income = client.get("/api/v1/reports/monthly-income?month=2026-01", headers=alice)
    assert income.status_code == 200, income.text
    assert Decimal(income.json()["salary_income"]) == Decimal("7000.00")
    assert Decimal(income.json()["non_salary_income"]) == Decimal("1000.00")
    assert Decimal(income.json()["total_income"]) == Decimal("8000.00")
    assert Decimal(income.json()["by_category"]["工资"]) == Decimal("7000.00")

    expenses = client.get("/api/v1/reports/monthly-expenses?month=2026-01", headers=alice)
    assert expenses.status_code == 200, expenses.text
    assert Decimal(expenses.json()["total_expense"]) == Decimal("1000.00")
    assert Decimal(expenses.json()["by_type"]["必要支出"]) == Decimal("900.00")
    assert Decimal(expenses.json()["by_type"]["弹性消费"]) == Decimal("100.00")


def test_progress_endpoints_and_dashboard_monthly_summary(client):
    headers = auth_headers(register_user(client, "progress@example.com"))
    client.put(
        "/api/v1/settings",
        headers=headers,
        json={"monthly_necessity_amount": "4000", "emergency_months": 3},
    )
    _post_transaction(client, headers, "应急金账户", "应急金", "2026-01-15", "3000")
    _post_transaction(client, headers, "债务还款账户", "信用卡/消费贷", "2026-01-20", "800")

    debt = client.post(
        "/api/v1/debts",
        headers=headers,
        json={
            "name": "信用卡分期",
            "current_balance": "10000",
            "annual_rate": "0.1800",
            "minimum_monthly_payment": "500",
            "extra_monthly_payment": "500",
        },
    )
    assert debt.status_code == 201, debt.text

    client.post(
        "/api/v1/asset-allocations",
        headers=headers,
        json={"asset_class": "权益基金/股票", "current_amount": "6000", "target_ratio": "0.6000"},
    )
    client.post(
        "/api/v1/asset-allocations",
        headers=headers,
        json={"asset_class": "现金及货币基金", "current_amount": "4000", "target_ratio": "0.4000"},
    )
    client.post(
        "/api/v1/goals",
        headers=headers,
        json={
            "name": "长期投资账户",
            "goal_type": "长期投资",
            "target_amount": "10000",
            "current_amount": "2500",
        },
    )

    emergency = client.get("/api/v1/emergency-fund/progress?month=2026-01", headers=headers)
    assert emergency.status_code == 200, emergency.text
    assert Decimal(emergency.json()["target_amount"]) == Decimal("12000.00")
    assert Decimal(emergency.json()["current_amount"]) == Decimal("3000.00")
    assert Decimal(emergency.json()["progress_rate"]) == Decimal("0.2500")

    debt_progress = client.get("/api/v1/debts/progress?month=2026-01", headers=headers)
    assert debt_progress.status_code == 200, debt_progress.text
    assert Decimal(debt_progress.json()["total_debt_balance"]) == Decimal("10000.00")
    assert Decimal(debt_progress.json()["planned_monthly_payment"]) == Decimal("1000.00")
    assert Decimal(debt_progress.json()["actual_debt_payment"]) == Decimal("800.00")
    assert Decimal(debt_progress.json()["repayment_completion_rate"]) == Decimal("0.8000")

    assets = client.get("/api/v1/asset-allocations/summary", headers=headers)
    assert assets.status_code == 200, assets.text
    assert Decimal(assets.json()["total_amount"]) == Decimal("10000.00")
    assert Decimal(assets.json()["items"][0]["current_ratio"]) == Decimal("0.6000")

    goals = client.get("/api/v1/goals/progress", headers=headers)
    assert goals.status_code == 200, goals.text
    assert Decimal(goals.json()["items"][0]["progress_rate"]) == Decimal("0.2500")

    dashboard = client.get("/api/v1/dashboard/monthly?month=2026-01", headers=headers)
    assert dashboard.status_code == 200, dashboard.text
    assert Decimal(dashboard.json()["emergency_fund_progress"]["progress_rate"]) == Decimal("0.2500")
    assert Decimal(dashboard.json()["emergency_fund_balance"]) == Decimal("3000.00")
    assert Decimal(dashboard.json()["debt_progress"]["repayment_completion_rate"]) == Decimal("0.8000")


def test_emergency_fund_progress_uses_plan_opening_balance_and_month_deposits(client):
    headers = auth_headers(register_user(client, "emergency-progress@example.com"))
    client.put(
        "/api/v1/settings",
        headers=headers,
        json={"monthly_necessity_amount": "4000", "emergency_months": 3},
    )
    _post_transaction(client, headers, "应急金账户", "应急金", "2025-12-15", "999")
    plan = client.post(
        "/api/v1/emergency-fund/plans",
        headers=headers,
        json={"month": "2026-01-01", "planned_amount": "1000", "opening_balance": "2000"},
    )
    assert plan.status_code == 201, plan.text
    _post_transaction(client, headers, "应急金账户", "应急金", "2026-01-15", "500")

    response = client.get("/api/v1/emergency-fund/progress?month=2026-01", headers=headers)

    assert response.status_code == 200, response.text
    assert Decimal(response.json()["target_amount"]) == Decimal("12000.00")
    assert Decimal(response.json()["planned_amount"]) == Decimal("1000.00")
    assert Decimal(response.json()["actual_month_deposit"]) == Decimal("500.00")
    assert Decimal(response.json()["current_amount"]) == Decimal("2500.00")
    assert Decimal(response.json()["progress_rate"]) == Decimal("0.2083")

    dashboard = client.get("/api/v1/dashboard/monthly?month=2026-01", headers=headers)
    assert dashboard.status_code == 200, dashboard.text
    assert Decimal(dashboard.json()["emergency_fund_balance"]) == Decimal("2500.00")


def test_debt_progress_does_not_invent_per_debt_payment_rates(client):
    headers = auth_headers(register_user(client, "debt-progress@example.com"))
    _post_transaction(client, headers, "债务还款账户", "信用卡/消费贷", "2026-01-20", "500")
    for name in ["信用卡分期", "消费贷"]:
        response = client.post(
            "/api/v1/debts",
            headers=headers,
            json={
                "name": name,
                "current_balance": "1000",
                "annual_rate": "0.1800",
                "minimum_monthly_payment": "500",
            },
        )
        assert response.status_code == 201, response.text

    response = client.get("/api/v1/debts/progress?month=2026-01", headers=headers)

    assert response.status_code == 200, response.text
    assert Decimal(response.json()["planned_monthly_payment"]) == Decimal("1000.00")
    assert Decimal(response.json()["actual_debt_payment"]) == Decimal("500.00")
    assert Decimal(response.json()["repayment_completion_rate"]) == Decimal("0.5000")
    assert [item["monthly_payment_progress_rate"] for item in response.json()["items"]] == [None, None]


def test_duplicate_resource_names_return_conflict(client):
    headers = auth_headers(register_user(client, "duplicates@example.com"))
    payload = {"name": "信用卡分期", "current_balance": "1000", "annual_rate": "0.1800"}

    created = client.post("/api/v1/debts", headers=headers, json=payload)
    duplicate = client.post("/api/v1/debts", headers=headers, json=payload)

    assert created.status_code == 201, created.text
    assert duplicate.status_code == 409
