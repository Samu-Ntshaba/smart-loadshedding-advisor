#!/usr/bin/env bash
set -euo pipefail

service="${SERVICE:-api}"

if [[ "$service" == "api" ]]; then
  exec uvicorn apps.api.app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
elif [[ "$service" == "ui" ]]; then
  exec streamlit run apps/ui/app.py --server.address 0.0.0.0 --server.port "${PORT:-8501}"
else
  echo "Unknown SERVICE value: $service (expected 'api' or 'ui')." >&2
  exit 1
fi
