import pytest
from sqlalchemy import select

from shared.storage import db
from shared.storage.models import AIRun, LLMCall
from worker.gateway.fake import FakeProvider
from worker.gateway.metering import metered_run
from worker.guardrails.schemas import Pong

class FailingProvider:
    name = "failing"

    async def run(self, agent, system, user, schema, tools=None):
        raise RuntimeError("boom")


async def create_run() -> int:
    async with db.SessionLocal() as session:
        run = AIRun(agent="ping", params={})
        session.add(run)
        await session.commit()
        return run.id


async def logged_calls() -> list[LLMCall]:
    async with db.SessionLocal() as session:
        return list(await session.scalars(select(LLMCall)))


async def test_successful_call_is_logged(test_db):
    run_id = await create_run()
    result = await metered_run(FakeProvider(), "ping", "system", "user", Pong, job_id=run_id, attempt=1)

    assert result.parsed == Pong(message="pong")
    calls = await logged_calls()
    assert len(calls) == 1
    call = calls[0]
    assert call.outcome == "ok"
    assert call.job_id == run_id
    assert call.attempt == 1
    assert call.agent == "ping"
    assert call.provider == "fake"
    assert call.model == "fake"
    assert call.latency_ms is not None
    assert call.error is None
    assert call.cost_eur is None


async def test_failed_call_is_logged_and_still_raises(test_db):
    run_id = await create_run()

    with pytest.raises(RuntimeError, match="boom"):
        await metered_run(FailingProvider(), "ping", "system", "user", Pong, job_id=run_id, attempt=1)

    calls = await logged_calls()
    assert len(calls) == 1
    call = calls[0]
    assert call.outcome == "api_error"
    assert "boom" in call.error
    assert call.provider == "failing"
    assert call.model is None
    calls = await logged_calls()
    assert len(calls) == 1
    call = calls[0]
    assert call.outcome == "api_error"
    assert "boom" in call.error
    assert call.provider == "failing"
    assert call.model is None
    assert "boom" in call.error
    assert call.provider == "failing"
    assert call.model is None
    assert call.model is None
    assert call.latency_ms is not None


async def test_broken_log_table_does_not_fail_the_call(test_db, monkeypatch):
    def broken_session():
        raise RuntimeError("database is down")

    monkeypatch.setattr(db, "SessionLocal", broken_session)

    result = await metered_run(FakeProvider(), "ping", "system", "user", Pong, job_id=1, attempt=1)

    assert result.parsed == Pong(message="pong")
