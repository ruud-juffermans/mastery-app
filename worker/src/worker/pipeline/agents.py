from collections.abc import Callable
from dataclasses import dataclass

from pydantic import BaseModel

from worker.context.prompts import Prompt, build_ping
from worker.guardrails.schemas import Pong


@dataclass
class Agent():
    build_prompt: Callable[[dict], Prompt]
    schema: type[BaseModel]


AGENTS: dict[str,Agent] = {
    "ping": Agent(build_prompt=build_ping, schema=Pong)
} 
