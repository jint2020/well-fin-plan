# Personal Finance MVP Design

## Goal

Build a multi-user personal finance web application based on the existing Excel template at `docs/个人资金管理模板_浮动收入版.xlsx`. The MVP turns the workbook's core logic into a FastAPI + PostgreSQL backend and a Vue 3 frontend.

Core financial order:

1. Cash-flow tracking
2. Emergency fund
3. Insurance/risk protection notes
4. High-interest debt cleanup
5. Long-term investing
6. Asset allocation optimization

## Approved Architecture Decisions

- Use FastAPI, SQLAlchemy 2.x, Pydantic, PostgreSQL, Alembic, Vue 3, Vite, TypeScript, Element Plus, and ECharts.
- Support multiple users from the first migration.
- All finance tables include `user_id`.
- Do not create physical database foreign keys.
- SQLAlchemy models are the schema source of truth.
- Alembic loads project model metadata and generates migrations from those models.
- Tests may create tables directly from `Base.metadata.create_all()` for isolated databases.
- No request body, query parameter, route parameter, or frontend state may determine the tenant boundary.

## Excel Mapping

| Workbook Sheet | Application Model |
| --- | --- |
| 参数设置 | `user_finance_settings`, `accounts`, `categories` |
| 流水记录 | `transactions` |
| 月度预算 | Calculated API projection |
| 月度仪表盘 | Calculated dashboard API projection |
| 收入规划 | Calculated income planning API projection |
| 应急金 | `emergency_fund_plans` plus emergency-fund transactions |
| 债务管理 | `debts` |
| 资产配置 | `asset_allocations` |
| 目标计划 | `financial_goals` |
| 使用说明, 资料来源 | Documentation only |

## Data Model

### Physical Constraint Policy

Tables use primary keys, unique constraints, check constraints where useful, and indexes. They do not use physical foreign keys. Columns such as `user_id`, `account_id`, and `category_id` are UUID references by convention, enforced by service-layer checks and tests.

SQLAlchemy model rules:

- Do not use `ForeignKey(...)`.
- Do not use `ForeignKeyConstraint(...)`.
- Do not rely on ORM relationships for authorization.
- Use explicit `where(Model.user_id == current_user.id)` filters in repositories/services.
- Add indexes on every `user_id` and common `(user_id, scope)` lookup.

### Tables

`users`

- `id uuid primary key`
- `email varchar unique not null`
- `password_hash varchar not null`
- `display_name varchar`
- `is_active boolean not null default true`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

`auth_sessions`

- `id uuid primary key`
- `user_id uuid not null indexed`
- `refresh_token_hash varchar not null`
- `expires_at timestamptz not null`
- `revoked_at timestamptz`
- `created_at timestamptz not null`

`user_finance_settings`

- `id uuid primary key`
- `user_id uuid not null unique indexed`
- `salary_min numeric(14,2) not null`
- `salary_max numeric(14,2) not null`
- `conservative_income_base numeric(14,2) not null`
- `necessity_ratio numeric(6,4) not null default 0.5`
- `saving_ratio numeric(6,4) not null default 0.3`
- `flex_ratio numeric(6,4) not null default 0.2`
- `extra_saving_ratio numeric(6,4) not null default 0.7`
- `extra_reserve_ratio numeric(6,4) not null default 0.2`
- `extra_flex_ratio numeric(6,4) not null default 0.1`
- `emergency_months integer not null default 3`
- `monthly_necessity_amount numeric(14,2) not null`
- `plan_year integer not null`

`accounts`

- `id uuid primary key`
- `user_id uuid not null indexed`
- `name varchar not null`
- `account_type varchar not null`
- `is_active boolean not null default true`
- Unique: `(user_id, name)`

`categories`

- `id uuid primary key`
- `user_id uuid not null indexed`
- `name varchar not null`
- `transaction_type varchar not null`
- `is_income boolean not null`
- `is_salary boolean not null default false`
- `sort_order integer not null default 0`
- Unique: `(user_id, transaction_type, name)`

`transactions`

- `id uuid primary key`
- `user_id uuid not null indexed`
- `account_id uuid not null indexed`
- `category_id uuid not null indexed`
- `occurred_on date not null`
- `month date not null`
- `transaction_type varchar not null`
- `counterparty varchar`
- `recurrence_type varchar`
- `description varchar`
- `amount numeric(14,2) not null`
- `note text`
- Indexes: `(user_id, month)`, `(user_id, occurred_on)`, `(user_id, transaction_type)`

`emergency_fund_plans`

- `id uuid primary key`
- `user_id uuid not null indexed`
- `month date not null`
- `planned_amount numeric(14,2) not null`
- `opening_balance numeric(14,2) not null default 0`
- `note text`
- Unique: `(user_id, month)`

`debts`

- `id uuid primary key`
- `user_id uuid not null indexed`
- `name varchar not null`
- `current_balance numeric(14,2) not null`
- `annual_rate numeric(8,6) not null`
- `minimum_monthly_payment numeric(14,2) not null default 0`
- `extra_monthly_payment numeric(14,2) not null default 0`
- `status varchar not null default 'active'`
- `note text`
- Unique: `(user_id, name)`

`asset_allocations`

- `id uuid primary key`
- `user_id uuid not null indexed`
- `asset_class varchar not null`
- `current_amount numeric(14,2) not null`
- `target_ratio numeric(6,4) not null`
- `risk_level varchar`
- `note text`
- Unique: `(user_id, asset_class)`

`financial_goals`

- `id uuid primary key`
- `user_id uuid not null indexed`
- `name varchar not null`
- `goal_type varchar not null`
- `target_amount numeric(14,2) not null`
- `current_amount numeric(14,2) not null default 0`
- `monthly_contribution numeric(14,2) not null default 0`
- `target_date date`
- `status varchar not null default 'active'`
- Unique: `(user_id, name)`

## Security Boundary

Authentication uses JWT access tokens and bcrypt password hashing. Every finance endpoint injects the current user through `get_current_user`.

Required query rule:

```python
where(Model.user_id == current_user.id)
```

Required write rule:

```python
model.user_id = current_user.id
```

Required update/delete rule:

```python
where(Model.id == resource_id, Model.user_id == current_user.id)
```

If a resource does not match the current user, return `404`, not `403`, to avoid leaking existence.

## Budget Calculation Rules

- Base daily budget uses `conservative_income_base`, not high-income months.
- Salary income is identified by `categories.is_salary == true`.
- Non-salary income is tracked separately.
- `extra_income = max(0, actual_total_income - conservative_income_base)`.
- Base budget:
  - Necessary: `conservative_income_base * 0.50`
  - Saving/investing/debt: `conservative_income_base * 0.30`
  - Flex spending: `conservative_income_base * 0.20`
- Extra income allocation:
  - Saving/investing/debt: `extra_income * 0.70`
  - Special reserve: `extra_income * 0.20`
  - Flex spending: `extra_income * 0.10`

## API Surface

Authentication:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/me`

Finance resources:

- `GET|POST /api/v1/transactions`
- `GET|PATCH|DELETE /api/v1/transactions/{id}`
- `GET|PUT /api/v1/settings`
- `GET|POST /api/v1/accounts`
- `GET|POST /api/v1/categories`
- `GET|POST /api/v1/emergency-fund/plans`
- `GET|POST /api/v1/debts`
- `GET|POST /api/v1/asset-allocations`
- `GET|POST /api/v1/goals`

Reports:

- `GET /api/v1/reports/monthly-budget?month=YYYY-MM`
- `GET /api/v1/reports/income-plan?year=YYYY`
- `GET /api/v1/dashboard/monthly?month=YYYY-MM`

## Test Requirements

- Passwords are stored as bcrypt hashes, never plaintext.
- Unauthenticated finance requests return `401`.
- User A cannot list user B's transactions.
- User A cannot read, update, or delete user B's transaction by ID.
- Repeat isolation tests for debts, asset allocations, and goals.
- Requests containing `user_id` are ignored or rejected by schemas.
- Monthly budget and dashboard statistics only include current-user data.
- Non-salary income increases extra allocation only and does not raise the conservative base budget.
