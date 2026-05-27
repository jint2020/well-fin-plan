# Personal Finance MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable multi-user personal finance MVP from the approved Excel-to-database design.

**Architecture:** FastAPI exposes authenticated finance APIs. SQLAlchemy 2.x declarative models define the schema, Alembic autogenerates migrations from `Base.metadata`, and no physical foreign keys are allowed. Vue 3 consumes the APIs and renders CRUD screens plus dashboard charts.

**Tech Stack:** Python 3.13, FastAPI, SQLAlchemy 2.x, Alembic, PostgreSQL, Pydantic, pytest, Vue 3, Vite, TypeScript, Element Plus, ECharts.

---

## Global Constraints

- Do not add `ForeignKey` or `ForeignKeyConstraint` anywhere.
- Do not accept `user_id` in finance request schemas.
- Every finance model includes `user_id` with an index.
- Every finance query filters by `current_user.id`.
- Return `404` for another user's resource ID.
- Review generated Alembic migrations before applying them and remove any accidental FK constraints.

## Target File Structure

```text
backend/
  alembic/
  app/
    api/
      deps.py
      v1/
        auth.py
        transactions.py
        reports.py
    core/
      config.py
      security.py
    db/
      base.py
      session.py
    models/
      user.py
      finance.py
    schemas/
      auth.py
      finance.py
    services/
      auth_service.py
      finance_service.py
      report_service.py
    main.py
  tests/
    test_auth.py
    test_user_isolation.py
    test_budget_reports.py
frontend/
  src/
    api/
    router/
    stores/
    views/
    components/
```

## Task 1: Backend Project Bootstrap

**Files:**

- Create: `backend/pyproject.toml`
- Create: `backend/app/main.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/db/base.py`
- Create: `backend/app/db/session.py`

- [ ] Add backend dependencies: FastAPI, Uvicorn, SQLAlchemy, Alembic, psycopg, Pydantic settings, python-jose or PyJWT, passlib with bcrypt, pytest, httpx.
- [ ] Create FastAPI app with `/api/v1/health`.
- [ ] Add settings for `DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, and token expiry.
- [ ] Add SQLAlchemy engine/session factory.
- [ ] Verify with `pytest` once tests are added.

## Task 2: SQLAlchemy Models Without Physical FKs

**Files:**

- Create: `backend/app/models/user.py`
- Create: `backend/app/models/finance.py`
- Modify: `backend/app/db/base.py`

- [ ] Define `Base(DeclarativeBase)`.
- [ ] Define all approved tables from the design spec.
- [ ] Use UUID primary keys.
- [ ] Add indexes for `user_id` and common user-scoped lookups.
- [ ] Add unique constraints such as `(user_id, name)`.
- [ ] Confirm there is no `ForeignKey` import or usage.

## Task 3: Alembic From Model Metadata

**Files:**

- Create/modify: `backend/alembic/env.py`
- Create: initial Alembic revision under `backend/alembic/versions/`

- [ ] Configure Alembic `target_metadata = Base.metadata`.
- [ ] Import all models in Alembic env so metadata is complete.
- [ ] Generate initial migration from models.
- [ ] Manually inspect migration for `sa.ForeignKeyConstraint`.
- [ ] Run migration against local PostgreSQL.

## Task 4: Authentication

**Files:**

- Create: `backend/app/core/security.py`
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/services/auth_service.py`
- Create: `backend/app/api/deps.py`
- Create: `backend/app/api/v1/auth.py`
- Test: `backend/tests/test_auth.py`

- [ ] Implement bcrypt password hashing and verification.
- [ ] Implement JWT creation and validation.
- [ ] Implement `get_current_user`.
- [ ] Add register, login, logout, and `/me`.
- [ ] Test plaintext password is never stored.
- [ ] Test unauthenticated finance access returns `401`.

## Task 5: Seed Per-User Defaults

**Files:**

- Modify: `backend/app/services/auth_service.py`
- Create: `backend/app/services/defaults.py`
- Test: `backend/tests/test_auth.py`

- [ ] After registration, create default finance settings from the Excel template.
- [ ] Create default accounts: 工资卡, 生活账户, 应急金账户, 投资账户, 快乐消费账户, 债务还款账户, 专项准备金账户.
- [ ] Create default categories including 工资, 奖金/绩效, 副业收入, 理财收益, 房租/房贷, 餐饮, 交通, 应急金, 基金定投, 信用卡/消费贷.
- [ ] Ensure defaults are scoped to the new user's `id`.

## Task 6: Transaction CRUD With User Isolation

**Files:**

- Create: `backend/app/schemas/finance.py`
- Create: `backend/app/services/finance_service.py`
- Create: `backend/app/api/v1/transactions.py`
- Test: `backend/tests/test_user_isolation.py`

- [ ] Create transaction schemas without `user_id`.
- [ ] On create, set `user_id` from `current_user.id`.
- [ ] Validate `account_id` and `category_id` belong to current user by explicit user-scoped queries.
- [ ] Implement list/read/update/delete with current-user filters.
- [ ] Test user A cannot list, read, update, or delete user B's transaction.

## Task 7: Monthly Budget and Income Reports

**Files:**

- Create: `backend/app/services/report_service.py`
- Create: `backend/app/api/v1/reports.py`
- Test: `backend/tests/test_budget_reports.py`

- [ ] Calculate salary income from categories where `is_salary = true`.
- [ ] Calculate non-salary income separately.
- [ ] Calculate actual income, extra income, budget allocations, actual spending, surplus, and saving/debt rate.
- [ ] Ensure all aggregate queries filter by `user_id`.
- [ ] Test extra income uses 70/20/10 without raising the conservative base budget.
- [ ] Test user B's income does not affect user A's report.

## Task 8: Emergency Fund, Debts, Assets, Goals

**Files:**

- Modify: `backend/app/schemas/finance.py`
- Create: API modules under `backend/app/api/v1/`
- Modify: `backend/app/services/finance_service.py`
- Test: `backend/tests/test_user_isolation.py`

- [ ] Add CRUD for emergency fund plans.
- [ ] Add CRUD for debts.
- [ ] Add CRUD for asset allocations.
- [ ] Add CRUD for financial goals.
- [ ] Repeat cross-user read/update/delete tests for each resource type.

## Task 9: Dashboard API

**Files:**

- Create: `backend/app/api/v1/dashboard.py`
- Modify: `backend/app/services/report_service.py`
- Test: `backend/tests/test_budget_reports.py`

- [ ] Return current month income, extra income, surplus, saving/debt rate, emergency fund progress, net assets, debt summary, and allocation summary.
- [ ] Keep the dashboard as a calculated projection, not a persisted table.

## Task 10: Vue MVP

**Files:**

- Create: `frontend/`
- Create: Vue views and API client modules.

- [ ] Initialize Vite Vue TypeScript app.
- [ ] Configure Element Plus and ECharts.
- [ ] Add login/register/logout flow.
- [ ] Store JWT client-side and attach it to API requests.
- [ ] Build views for transactions, monthly budget, dashboard, debts, asset allocation, emergency fund, and goals.
- [ ] Do not use frontend `user_id` for security decisions.

## Task 11: End-to-End Verification

- [ ] Run backend tests.
- [ ] Run Alembic migration on an empty PostgreSQL database.
- [ ] Start FastAPI locally.
- [ ] Start Vue locally.
- [ ] Register two users and manually verify data isolation.
- [ ] Create sample transactions matching the Excel examples and compare monthly budget outputs.

## Official References

- SQLAlchemy 2.x declarative mapping: https://docs.sqlalchemy.org/en/20/orm/declarative_mapping.html
- Alembic autogenerate from model metadata: https://alembic.sqlalchemy.org/en/latest/autogenerate.html
- FastAPI OAuth2/JWT/password hashing pattern: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- Pydantic settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
