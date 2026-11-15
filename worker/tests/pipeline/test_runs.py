from sqlalchemy import select

from shared.storage import db
from shared.storage.models import AIRun, LLMCall
from worker.gateway.fake import FakeProvider
from worker.pipeline.runs import execute_ai_run, fail_run, release_run

class FailingProvider:
    name = "failing"

    async def run(self, agent, system, user, schema, tools=None):
        raise RuntimeError("boom")


async def create_run(agent: str) -> int:
    async with db.SessionLocal() as session:
        run = AIRun(agent=agent, params={})
        session.add(run)
        await session.commit()
        return run.id


async def execute(run_id: int, provider) -> AIRun:
    async with db.SessionLocal() as session:
        await execute_ai_run(session, run_id, provider)
    async with db.SessionLocal() as session:
        return await session.get(AIRun, run_id)

async def test_successful_run_is_logged_in_full(test_db):
    run = await execute(await create_run("ping"), FakeProvider())
    
    assert run.status == "ok"
    assert run.output == {"message": "pong"}
    assert run.prompt == {"system": "You are a helpful assistant.", "user": "ping"}
    assert run.provider == "fake"
    assert run.model == "fake"
    assert run.raw == '{"message": "pong"}'
    assert run.duration_ms is not None
    assert run.error is None

    async with db.SessionLocal() as session:
        calls = list(await session.scalars(select(LLMCall).where(LLMCall.job_id == run.id)))
    assert len(calls) == 1
    assert calls[0].outcome == "ok"
    assert calls[0].attempt == 1


async def test_failing_provider_yields_error(test_db):
    run = await execute(await create_run("ping"), FailingProvider())

    assert run.status == "error"
    assert "boom" in run.error
    assert run.prompt is not None
    assert run.output is None


async def test_unknown_agent_yields_error(test_db):
    provider = FakeProvider()

    run = await execute(await create_run("nope"), provider)

    assert run.status == "error"
    assert "nope" in run.error
    assert provider.calls == []


async def test_missing_row_does_nothing(test_db):
    async with db.SessionLocal() as session:
        await execute_ai_run(session, 999, FakeProvider())


async def create_run_with_status(status: str) -> int:
    async with db.SessionLocal() as session:
        run = AIRun(agent="ping", params={}, status=status)
        session.add(run)
        await session.commit()
        return run.id


async def get_run(run_id: int) -> AIRun:
    async with db.SessionLocal() as session:
        return await session.get(AIRun, run_id)


async def test_fail_run_marks_a_running_job_as_error(test_db):
    run_id = await create_run_with_status("running")

    async with db.SessionLocal() as session:
        await fail_run(session, run_id, "timed out")

    run = await get_run(run_id)
    assert run.status == "error"
    assert run.error == "timed out"


async def test_release_run_hands_a_running_job_back(test_db):
    run_id = await create_run_with_status("running")

    async with db.SessionLocal() as session:
        await release_run(session, run_id)

    run = await get_run(run_id)
    assert run.status == "queued"

async def test_finished_job_is_left_alone(test_db):
    run_id = await create_run_with_status("ok")

    async with db.SessionLocal() as session:
        await fail_run(session, run_id, "timed out")
        await release_run(session, run_id)

    run = await get_run(run_id)
    assert run.status == "ok"
    assert run.error is None