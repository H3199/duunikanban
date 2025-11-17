from fastapi.testclient import TestClient
from api.main import app
from api.store import persist_job

client = TestClient(app)

def test_list_jobs_returns_state():
    # Arrange: simulate persisted state
    persist_job(123, "applied", "test note")

    # Act
    res = client.get("/jobs")
    data = res.json()

    # Assert
    assert res.status_code == 200
    assert any(j["id"] == 123 and j["state"] == "applied" for j in data)
