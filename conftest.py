import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker,create_async_engine

from shared.storage import db
from shared.storage.models import Base


@pytest.fixture
async def test_db(tmp_path, monkeypatch):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'test.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    monkeypatch.setattr(db, "engine", engine)
    monkeypatch.setattr(db, "SessionLocal", async_sessionmaker(engine, expire_on_commit=False))

    yield engine

    await engine.dispose()
