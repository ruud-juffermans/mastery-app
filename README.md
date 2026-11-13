# Mastery App

A personal, AI-driven learning system. Pick a subject, the AI interviews you, builds a learning path, curates sources
for each step, examines you, grades you and decides what comes next. Everything is stored; progress is gamified with XP,
levels, streaks, badges and a skill tree.

## Getting started

Requires Docker with Compose.

1. Copy the example environment file: `cp .env.example .env`
2. Start the stack: `make up`
3. Check that the API answers: `curl localhost:8000/api/health`

Other commands:

- `make down` stops the stack
- `make logs` follows the logs of all services
- `make test` runs the tests

The project is under construction: the stack itself arrives in a later commit.
