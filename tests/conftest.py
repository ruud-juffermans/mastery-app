import pytest
from httpx import ASGITransport, AsyncClient

from api import queue
from api.main import app
from shared.storage import db
from worker.gateway.fake import FakeProvider
from worker.pipeline.runs import execute_ai_run


class InlineBackend:
    """Runs the job on the spot, inside the request: no Redis and no worker process."""

    async def submit(self, run_id: int) -> None:
        async with db.SessionLocal() as session:
            await execute_ai_run(session, run_id, FakeProvider())


@pytest.fixture
def inline_backend():
    previous = queue._backend
    queue.set_backend(InlineBackend())
    yield
    queue.set_backend(previous)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
