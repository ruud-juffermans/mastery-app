from api.health import check_redis
from api.main import app


async def test_health(client, test_db):
    async def redis_ok() -> str:
        return "ok"

    app.dependency_overrides[check_redis] = redis_ok
    try:
        response = await client.get("/api/health")
    finally:
        app.dependency_overrides.pop(check_redis)

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": "ok", "redis": "ok"}