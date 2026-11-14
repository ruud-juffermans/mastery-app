import logging
import time

from sqlalchemy.ext.asyncio import AsyncSession

from shared.storage.models import AIRun
from worker.gateway.base import AIProvider, InvalidOutputError
from worker.pipeline.agents import AGENTS

logger = logging.getLogger(__name__)


async def execute_ai_run(session: AsyncSession, run_id: int, provider: AIProvider) -> None:
    run = await session.get(AIRun, run_id)
    if run is None:
        logger.warning(f"Run {run_id} not found")
        return
    
    run.status = "running"
    await session.commit()

    try:
        agent = AGENTS[run.agent]
        prompt = agent.build_prompt(run.params or {})
        run.prompt = {"system": prompt.system, "user": prompt.user}

        start_time = time.perf_counter()
        result = await provider.run(run.agent, prompt.system, prompt.user, agent.schema)
        run.duration_ms = int((time.perf_counter() - start_time) * 1000)

        run.output = result.parsed.model_dump()
        run.raw = result.raw
        run.provider = provider.name
        run.model = result.model
        run.tokens_in = result.tokens_in
        run.tokens_out = result.tokens_out
        run.status = "ok"
    except Exception as e:
        run.status = "error"
        run.error = f"{type(e).__name__}: {e}"
        if isinstance(e, InvalidOutputError):
            run.raw = e.raw

    await session.commit()
    

