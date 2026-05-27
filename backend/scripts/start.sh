#!/usr/bin/env sh
set -eu

uv run --no-dev --no-sync alembic upgrade head
exec uv run --no-dev --no-sync uvicorn app.main:app --host 0.0.0.0 --port 8000
