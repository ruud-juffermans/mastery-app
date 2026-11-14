async def test_health(client, test_db):
    response = await client.get("/api/health")
    
    assert response.status_code == 200
    assert response.json() == {'status': 'ok', 'db': 'ok'}
