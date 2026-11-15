
import asyncio

from arq import func
from arq.connections import RedisSettings

from shared.jobs import RUN_AI_JOB
from shared.storage import db
from worker.config import config
from worker.gateway.fake import FakeProvider
from worker.pipeline.runs import execute_ai_run, fail_run, release_run

async def startup(ctx: dict) -> None:
      """arq passes this `ctx` to every job, so the provider is created once per worker."""
      ctx["provider"] = FakeProvider()


async def run_ai_job(ctx: dict, run_id: int) -> str:
    """Run one job under our own deadline, and never leave it `running` when we stop working on it:
    a timeout marks it failed (a human decides about a retry; an automatic one would pay twice for a
    call that is probably slow again), a worker shutdown hands it back to the queue."""
    try:
        async with db.SessionLocal() as session:
            await asyncio.wait_for(execute_ai_run(session, run_id, ctx["provider"]), timeout=config.ai_job_timeout_s)
    except TimeoutError:
        async with db.SessionLocal() as session:
            await fail_run(session, run_id, f"TimeoutError: job did not finish within {config.ai_job_timeout_s}s")
    except asyncio.CancelledError:
        async with db.SessionLocal() as session:
            await release_run(session, run_id)
        raise


class WorkerSettings:
    functions = [func(run_ai_job, name=RUN_AI_JOB)]
    redis_settings = RedisSettings.from_dsn(config.redis_url)
    on_startup = startup
    # arq's own timeout is only the backstop; `run_ai_job` enforces the real deadline and cleans up after it.
    job_timeout = config.ai_job_timeout_s + 10
