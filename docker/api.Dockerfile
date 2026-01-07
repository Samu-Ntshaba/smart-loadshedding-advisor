FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml /app/pyproject.toml

RUN UV_SYSTEM_PYTHON=1 uv sync --no-dev

COPY . /app

EXPOSE 8000

CMD ["/bin/sh", "-c", "alembic -c apps/api/alembic.ini upgrade head && uvicorn apps.api.app.main:app --host 0.0.0.0 --port 8000"]
