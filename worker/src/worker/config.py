from shared.config import Settings


class WorkerConfig(Settings):
    """Configuration for the worker process."""

    ai_job_timeout_s: int = 120


config = WorkerConfig()
