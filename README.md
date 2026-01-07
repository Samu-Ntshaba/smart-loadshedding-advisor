# Smart Loadshedding Advisor

Scaffold for a FastAPI + Streamlit project that will later integrate EskomSePush and AI-driven insights.

## Quickstart (Docker)

1. Copy env file and set values:
   ```bash
   cp .env.example .env
   ```
2. Build and run:
   ```bash
   docker compose up --build
   ```
3. Verify:
   - API: http://localhost:8000/health
   - UI: http://localhost:8501

## Quickstart (Without Docker, using uv)

1. Create venv and activate:
   ```bash
   uv venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Run API:
   ```bash
   scripts/dev_api.sh
   ```
4. Run UI (new terminal):
   ```bash
   scripts/dev_ui.sh
   ```

## Environment Variables

Set these in `.env` (see `.env.example`):

- `ESKOM_TOKEN_KEY`: EskomSePush API token (placeholder for Phase 2).
- `OPENAI_KEY`: OpenAI API key (placeholder for Phase 2).
- `DATABASE_URL`: Postgres connection string.
- `API_BASE_URL`: Base URL for the API used by Streamlit (defaults to `http://localhost:8000`).

## Folder Structure

```
smart-loadshedding-advisor/
  apps/
    api/                # FastAPI service
    ui/                 # Streamlit UI
  docker/               # Dockerfiles
  scripts/              # Local dev scripts
```

## Notes

Phase 2 will add EskomSePush integration, AI prompts, and analytics logic. This scaffold only includes mock endpoints and placeholder models.
