import pytest

from api import queue
from shared.storage import db
from shared.storage.models import AIRun


class RecordingBackend:
    """Remembers what was submitted and runs nothing."""

    def __init__(self) -> None:
        self.submitted: list[int] = []

    async def submit(self, run_id: int) -> None:
        self.submitted.append(run_id)


@pytest.fixture
def backend():
    previous = queue._backend
    recording = RecordingBackend()
    queue.set_backend(recording)
    yield recording
    queue.set_backend(previous)


async def test_ping_is_queued(client, test_db, backend):
    r = await client.post("/api/jobs/ping")
    assert r.status_code == 202
    job = r.json()
    assert job["status"] == "queued"
    assert job["agent"] == "ping"
    async with db.SessionLocal() as session:
        run = await session.get(AIRun, job["id"])
    assert run is not None
    assert backend.submitted == [job["id"]]


async def test_get_job(client, test_db, backend):
    job = (await client.post("/api/jobs/ping")).json()

    r = await client.get(f"/api/jobs/{job['id']}")
    assert r.status_code == 200
    assert r.json() == job


async def test_unknown_job_is_404(client, test_db):
    r = await client.get("/api/jobs/999")
    assert r.status_code == 404