async def test_ping_runs_end_to_end(client, test_db, inline_backend):
    response = await client.post("/api/jobs/ping")
    assert response.status_code == 202
    job = response.json()
    print(job)
    assert job["status"] == "ok"
    assert job["output"] == {"message": "pong"}

    response = await client.get(f"/api/jobs/{job['id']}")
    assert response.json()["provider"] == "fake"