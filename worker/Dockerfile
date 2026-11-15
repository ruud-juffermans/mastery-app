FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /bin/uv

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock .python-version ./
COPY shared/pyproject.toml shared/
COPY worker/pyproject.toml worker/
RUN uv sync --frozen --package worker --no-dev --no-install-workspace

COPY shared/ shared/
COPY worker/ worker/
RUN uv sync --frozen --package worker --no-dev

CMD ["arq", "worker.main.WorkerSettings"]