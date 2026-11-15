"""Job endpoints: the frontend polls `GET /api/jobs/{id}` while the worker runs an AI call."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.queue import enqueue
from shared.storage.db import get_session
from shared.storage.models import AIRun

router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobOut(BaseModel):
    id: int
    agent: str
    provider: str | None
    model: str | None
    status: str
    output: dict[str, Any] | None
    error: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("/{job_id}", response_model=JobOut)
async def get_job(job_id: int, session: AsyncSession = Depends(get_session)):
    run = await session.get(AIRun, job_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return run


@router.post("/ping", response_model=JobOut, status_code=202)
async def ping_job(session: AsyncSession = Depends(get_session)):
    """Smoke test for the queue: enqueues a trivial AI run and returns it for polling."""
    return await enqueue(session, "ping", {})
