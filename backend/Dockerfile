FROM ghcr.io/astral-sh/uv:0.9.30-python3.14-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY alembic.ini ./alembic.ini
COPY alembic ./alembic
COPY app ./app
COPY scripts ./scripts

RUN chmod +x /app/scripts/start.sh

EXPOSE 8000
CMD ["/app/scripts/start.sh"]
