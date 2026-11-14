from dataclasses import dataclass
from typing import Protocol

from pydantic import BaseModel, ValidationError


@dataclass
class ProviderResult:
    parsed: BaseModel
    raw: str
    model: str
    tokens_in: int
    tokens_out: int

class AIProvider(Protocol):
    name: str
    
    async def run(self, 
        agent: str, 
        system: str, 
        user: str, 
        schema: type[BaseModel], 
        tools: list | None = None
    ) -> ProviderResult:
        ...

class InvalidOutputError(Exception):
    def __init__(self, raw: str, validation_error: ValidationError):
        super().__init__(f"model output did not match the schema: {validation_error}")
        self.raw = raw
        self.validation_error = validation_error
