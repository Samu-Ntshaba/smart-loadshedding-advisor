FROM python:3.12-slim

WORKDIR /app

# Install uv (dependency manager)
RUN pip install --no-cache-dir uv

# Copy dependency files first for Docker layer caching
COPY pyproject.toml uv.lock /app/

# Install runtime dependencies into the system python (container)
RUN UV_SYSTEM_PYTHON=1 uv sync --no-dev

# Copy the rest of the project
COPY . /app

EXPOSE 8000

# Run migrations then start FastAPI
CMD ["/bin/sh", "-c", "alembic -c apps/api/alembic.ini upgrade head && uvicorn apps.api.app.main:app --host 0.0.0.0 --port 8000"]
