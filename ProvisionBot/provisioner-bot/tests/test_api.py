import pytest

async def test_validate_approved(client):
    res = await client.post("/api/validate", json={"env_type": "docker", "env_name": "dev"})
    assert res.status_code == 200
    assert res.json()["status"] == "approved"

async def test_validate_rejected_env(client):
    res = await client.post("/api/validate", json={"env_type": "docker", "env_name": "production"})
    assert res.status_code == 200
    assert res.json()["status"] == "rejected"

async def test_validate_rejected_type(client):
    res = await client.post("/api/validate", json={"env_type": "kubernetes", "env_name": "dev"})
    assert res.status_code == 200
    assert res.json()["status"] == "rejected"

async def test_submit_request(client):
    res = await client.post("/api/submit", json={
        "requester": "TestUser",
        "env_type": "docker",
        "env_name": "dev",
        "details": "Create Docker environment with postgres and redis"
    })
    assert res.status_code == 200
    assert "request_id" in res.json()

async def test_get_requests(client):
    res = await client.get("/api/requests")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

async def test_chat_mock(client):
    res = await client.post("/api/chat", json={
        "message": "How do I create a Docker environment?",
        "history": []
    })
    assert res.status_code == 200
    assert "reply" in res.json()

async def test_status_endpoint(client):
    res = await client.get("/api/status")
    assert res.status_code == 200
    assert "mock_mode" in res.json()
