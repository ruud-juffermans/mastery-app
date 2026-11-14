import json

from pydantic import BaseModel, ValidationError

from worker.gateway.base import InvalidOutputError, ProviderResult

DEFAULT_FIXTURES = {"ping": {"message": "pong"}}

class FakeProvider:
    name = "fake"
    
    def __init__(self, fixtures: dict[str, dict] | None = None):
        self.fixtures = DEFAULT_FIXTURES if fixtures is None else fixtures
        self.calls: list[dict] = []

    async def run(
        self, 
        agent:str, 
        system:str, 
        user:str, 
        schema: type[BaseModel], 
        tools: list| None = None
    ) -> ProviderResult:
        self.calls.append(
            {
                "agent": agent,
                "system": system,
                "user": user
            }
        )

        raw = json.dumps(self.fixtures.get(agent, {}))
        try:
            parsed = schema.model_validate_json(raw)
        except ValidationError as e:
            raise InvalidOutputError(raw=raw, validation_error=e) from e
        return ProviderResult(
            parsed=parsed,
            raw=raw,
            model="fake",
            tokens_in=0,
            tokens_out=0,
        )
