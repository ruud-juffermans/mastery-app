FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /bin/uv

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock .python-version ./
COPY shared/pyproject.toml shared/
COPY api/pyproject.toml api/
RUN uv sync --frozen --package api --no-dev --no-install-workspace

COPY shared/ shared/
COPY api/ api/
RUN uv sync --frozen --package api --no-dev

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]