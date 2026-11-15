import json
import logging
import time

from pydantic import BaseModel

from shared.storage import db
from shared.storage.models import LLMCall
from worker.gateway.base import AIProvider, ProviderResult

logger = logging.getLogger(__name__)
call_log = logging.getLogger("llm_calls")


async def record_call(record: dict) -> None:
    """Log one provider call: a JSON line first, then a row in its own transaction."""
    call_log.info(json.dumps(record))
    try:
        async with db.SessionLocal() as session:
            session.add(LLMCall(**record))
            await session.commit()
    except Exception:
        logger.exception("Could not write the llm_calls row.")


async def metered_run(
        provider: AIProvider, 
        agent: str, 
        system: str, 
        user: str, 
        schema: type[BaseModel], 
        tools: list | None = None,
        *,
        job_id: int,
        attempt: int
    ) -> ProviderResult:
    """Call the provider and log the call. Returns or raies exactly what the provder did."""
    record = {
        "job_id": job_id,
        "agent": agent,
        "attempt": attempt,
        "provider": provider.name,
        "model": None,
        "input_tokens": None,
        "output_tokens": None,
        "cache_read_tokens": None,
        "error": None,
    }
    start = time.perf_counter()
    try: 
        result = await provider.run(agent, system, user, schema, tools)
    except Exception as e:
        record["outcome"] = "api_error"
        record["error"] = f"{type(e).__name__}: {e}"
        raise
    else:
        record["outcome"] = "ok"
        record["model"] = result.model
        record["input_tokens"] = result.tokens_in
        record["output_tokens"] = result.tokens_out
        return result
    finally:
        record["latency_ms"] = int((time.perf_counter() - start) * 1000)
        if "outcome" in record:
            await record_call(record)
