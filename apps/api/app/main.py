from fastapi import FastAPI

from apps.api.app.routers import advisor, eskom_stub, health

app = FastAPI(title="Smart Loadshedding Advisor API")

app.include_router(health.router)
app.include_router(eskom_stub.router)
app.include_router(advisor.router)
