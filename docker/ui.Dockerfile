FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml /app/pyproject.toml

RUN UV_SYSTEM_PYTHON=1 uv sync --no-dev

COPY . /app

EXPOSE 8501

CMD ["streamlit", "run", "apps/ui/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
