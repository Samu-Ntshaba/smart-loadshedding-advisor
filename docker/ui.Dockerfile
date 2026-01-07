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

EXPOSE 8501

# Run Streamlit UI
CMD ["streamlit", "run", "apps/ui/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
