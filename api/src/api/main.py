from fastapi import FastAPI

from api.health import router as health_router
from api.jobs import router as jobs_router


app = FastAPI(title="Mastery App API", version="0.1.0")
app.include_router(health_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")