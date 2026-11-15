from datetime import datetime
from decimal import Decimal

from sqlalchemy import Integer, String, JSON, Text,DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# JSONB on Postgres; plain JSON elsewhere (tests run on SQLite).
JSONType = JSON().with_variant(JSONB(), "postgresql")

class Base(DeclarativeBase):
    pass

class AIRun(Base):
    """One job: a model call (with its retries) plus the handler that stores the result."""

    __tablename__ = "ai_run"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent: Mapped[str] = mapped_column(String(32))
    provider: Mapped[str | None] = mapped_column(String(32))
    model: Mapped[str | None] = mapped_column(String(128))
    params: Mapped[dict | None] = mapped_column(JSONType)
    prompt: Mapped[dict | None] = mapped_column(JSONType)
    output: Mapped[dict | None] = mapped_column(JSONType)
    raw: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="queued", server_default="queued")
    error: Mapped[str | None] = mapped_column(Text)
    tokens_in: Mapped[int | None] = mapped_column(Integer)
    tokens_out: Mapped[int | None] = mapped_column(Integer)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
