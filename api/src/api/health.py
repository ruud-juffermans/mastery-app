import asyncio

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import text

router = APIRouter()

class Health(BaseModel):
    status: str
    db: str

async def check_db() -> str:
    from shared.storage.db import engine

    try:
        async with engine.connect() as conn:
            await asyncio.wait_for(conn.execute(text("SELECT 1")), timeout=3)
        return "ok"
    except Exception as exc:  # noqa: BLE001
        return f"error: {type(exc).__name__}"

@router.get("/health")
async def health(db: str = Depends(check_db)):
    body = Health(status="ok" if db == "ok" else "degraded", db=db)
    code = 200 if body.status == "ok" else 503
    return JSONResponse(status_code=code, content=body.model_dump())