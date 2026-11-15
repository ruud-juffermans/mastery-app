from typing import Protocol

from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from shared.config import settings
from shared.jobs import RUN_AI_JOB
from shared.storage.models import AIRun

class JobBackend(Protocol):
    async def submit(self, run_id: int) -> None: ...

class ArqBackend:
    def __init__(self) -> None:
        self._pool: ArqRedis | None = None

    async def pool(self) -> ArqRedis:
        if self._pool is None:
            self._pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
        return self._pool

    async def submit(self, run_id: int) -> None:
        await (await self.pool()).enqueue_job(RUN_AI_JOB, run_id)
    
_backend: JobBackend | None = None


def get_backend() -> JobBackend:
    global _backend
    if _backend is None:
        _backend = ArqBackend()
    return _backend


def set_backend(backend: JobBackend | None) -> None:
    global _backend
    _backend = backend


async def enqueue(session, agent: str, params: dict) -> AIRun:
    run = AIRun(agent=agent, params=params)
    session.add(run)
    await session.commit()

    try:
        await get_backend().submit(run.id)
    except Exception as e:
        run.status = "error"
        run.error = f"could not enqueue: {e}"
        await session.commit()
        raise

    await session.refresh(run)
    return run