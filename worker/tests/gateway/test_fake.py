import pytest

from worker.gateway.base import InvalidOutputError
from worker.gateway.fake import FakeProvider
from worker.guardrails.schemas import Pong


async def test_returns_a_validated_pong():
    result = await FakeProvider().run("ping", "system text", "user text", Pong)

    assert result.parsed == Pong(message="pong")
    assert result.model == "fake"


async def test_agent_without_fixture_raises():
    with pytest.raises(InvalidOutputError) as excinfo:
        await FakeProvider().run("unknown", "system text", "user text", Pong)

    assert excinfo.value.raw == "{}"


async def test_records_every_call():
    provider = FakeProvider()

    await provider.run("ping", "system text", "user text", Pong)

    assert provider.calls == [{"agent": "ping", "system": "system text", "user": "user text"}]
