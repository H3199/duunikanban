import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.store import load_state

client = TestClient(app)

def test_change_job_state(tmp_path, monkeypatch):
    monkeypatch.setenv("STATE_FILE", str(tmp_path / "job_state.json"))

    response = client.post("/jobs/123", json={"state": "applied", "notes": "Sent CV"})
    assert response.status_code == 200

    json_data = load_state()
    assert "123" in json_data
    assert json_data["123"]["state"] == "applied"
    assert json_data["123"]["notes"] == "Sent CV"
