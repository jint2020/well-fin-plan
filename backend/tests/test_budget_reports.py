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


def test_extra_income_allocation_does_not_raise_base_daily_budget(client):
    headers = auth_headers(register_user(client, "alice@example.com"))

    _post_transaction(client, headers, "工资卡", "工资", "2026-01-05", "7800")
    _post_transaction(client, headers, "工资卡", "副业收入", "2026-01-12", "800")
    _post_transaction(client, headers, "工资卡", "奖金/绩效", "2026-01-20", "500")
    _post_transaction(client, headers, "生活账户", "餐饮", "2026-01-08", "900")
    _post_transaction(client, headers, "应急金账户", "应急金", "2026-01-15", "1200")
    _post_transaction(client, headers, "债务还款账户", "信用卡/消费贷", "2026-01-22", "900")

    response = client.get("/api/v1/reports/monthly-budget?month=2026-01", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()

    assert Decimal(data["salary_income"]) == Decimal("7800.00")
    assert Decimal(data["non_salary_income"]) == Decimal("1300.00")
    assert Decimal(data["actual_total_income"]) == Decimal("9100.00")
    assert Decimal(data["necessary_budget"]) == Decimal("3500.00")
    assert Decimal(data["base_saving_budget"]) == Decimal("2100.00")
    assert Decimal(data["base_flex_budget"]) == Decimal("1400.00")
    assert Decimal(data["extra_income"]) == Decimal("1300.00")
    assert Decimal(data["extra_to_saving_debt"]) == Decimal("910.00")
    assert Decimal(data["extra_to_reserve"]) == Decimal("260.00")
    assert Decimal(data["extra_to_flex"]) == Decimal("130.00")
    assert Decimal(data["recommended_saving_debt"]) == Decimal("3010.00")
    assert Decimal(data["recommended_flex"]) == Decimal("1530.00")


def test_salary_above_conservative_base_is_not_extra_income(client):
    headers = auth_headers(register_user(client, "alice@example.com"))

    _post_transaction(client, headers, "工资卡", "工资", "2026-01-05", "8136")

    response = client.get("/api/v1/reports/monthly-budget?month=2026-01", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()

    assert Decimal(data["salary_income"]) == Decimal("8136.00")
    assert Decimal(data["non_salary_income"]) == Decimal("0.00")
    assert Decimal(data["actual_total_income"]) == Decimal("8136.00")
    assert Decimal(data["budget_income"]) == Decimal("7000.00")
    assert Decimal(data["extra_income"]) == Decimal("0.00")
    assert Decimal(data["extra_to_saving_debt"]) == Decimal("0.00")
    assert Decimal(data["extra_to_reserve"]) == Decimal("0.00")
    assert Decimal(data["extra_to_flex"]) == Decimal("0.00")


def test_monthly_report_only_uses_current_user_data(client):
    alice = auth_headers(register_user(client, "alice@example.com"))
    bob = auth_headers(register_user(client, "bob@example.com"))

    _post_transaction(client, alice, "工资卡", "工资", "2026-01-05", "7000")
    _post_transaction(client, bob, "工资卡", "工资", "2026-01-05", "99999")

    response = client.get("/api/v1/reports/monthly-budget?month=2026-01", headers=alice)
    assert response.status_code == 200, response.text
    assert Decimal(response.json()["salary_income"]) == Decimal("7000.00")


def test_dashboard_is_scoped_to_current_user(client):
    alice = auth_headers(register_user(client, "alice@example.com"))
    bob = auth_headers(register_user(client, "bob@example.com"))

    _post_transaction(client, alice, "工资卡", "工资", "2026-01-05", "7000")
    _post_transaction(client, bob, "工资卡", "工资", "2026-01-05", "20000")

    response = client.get("/api/v1/dashboard/monthly?month=2026-01", headers=alice)
    assert response.status_code == 200, response.text
    assert Decimal(response.json()["monthly_budget"]["salary_income"]) == Decimal("7000.00")


def test_income_plan_is_scoped_to_current_user(client):
    alice = auth_headers(register_user(client, "alice@example.com"))
    bob = auth_headers(register_user(client, "bob@example.com"))

    _post_transaction(client, alice, "工资卡", "工资", "2026-01-05", "7000")
    _post_transaction(client, bob, "工资卡", "工资", "2026-01-05", "20000")

    response = client.get("/api/v1/reports/income-plan?year=2026", headers=alice)
    assert response.status_code == 200, response.text
    january = response.json()["months"][0]
    assert Decimal(january["salary_income"]) == Decimal("7000.00")
