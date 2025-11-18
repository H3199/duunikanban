from fastapi.testclient import TestClient
from api.main import app
from myclasses import JobState
from api.store import persist_job

client = TestClient(app)


def test_move_job():
    # Setup initial state
    persist_job(123, JobState.NEW, "initial note")

    # Act: move to 'applied'
    res = client.post("/jobs/123/move/applied")
    data = res.json()

    assert res.status_code == 200
    assert data["id"] == 123
    assert data["state"] == "applied"
    assert data["notes"] == "initial note"

    # Confirm persisted change via GET
    list_res = client.get("/jobs")
    listing = list_res.json()

    assert any(j["state"] == "applied" for j in listing)
