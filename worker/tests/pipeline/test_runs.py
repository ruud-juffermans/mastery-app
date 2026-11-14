from shared.storage import db
from shared.storage.models import AIRun
from worker.gateway.fake import FakeProvider
from worker.pipeline.runs import execute_ai_run

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
