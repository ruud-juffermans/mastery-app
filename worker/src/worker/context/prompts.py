from dataclasses import dataclass

@dataclass
class Prompt:
    system: str
    user: str

def build_ping(params: dict) -> Prompt:
    return Prompt(
        system="You are a helpful assistant.",
        user="ping"
    )
