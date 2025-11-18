import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.store import load_state

client = TestClient(app)


# The different states of a job:
#
# NEW
# SAVED
# APPLIED
# INTERVIEW
# REJECTED
# OFFER
# TRASH
#

def test_apply_job(tmp_path, monkeypatch):
    monkeypatch.setenv("STATE_FILE", str(tmp_path / "job_state.json"))

    response = client.post("/jobs/123", json={"state": "applied", "notes": "Sent CV"})
    assert response.status_code == 200

    json_data = load_state()
    assert "123" in json_data
    assert json_data["123"]["state"] == "applied"
    assert json_data["123"]["notes"] == "Sent CV"


def test_trash_job(tmp_path, monkeypatch):
    monkeypatch.setenv("STATE_FILE", str(tmp_path / "job_state.json"))

    response = client.post("/jobs/123", json={"state": "trash", "notes": "not interested"})
    assert response.status_code == 200

    json_data = load_state()
    assert "123" in json_data
    assert json_data["123"]["state"] == "trash"
    assert json_data["123"]["notes"] == "not interested"


def test_reject_job(tmp_path, monkeypatch):
    monkeypatch.setenv("STATE_FILE", str(tmp_path / "job_state.json"))

    response = client.post("/jobs/123", json={"state": "rejected", "notes": "Not enough Python skills"})
    assert response.status_code == 200

    json_data = load_state()
    assert "123" in json_data
    assert json_data["123"]["state"] == "rejected"
    assert json_data["123"]["notes"] == "Not enough Python skills"


def test_interview_job(tmp_path, monkeypatch):
    monkeypatch.setenv("STATE_FILE", str(tmp_path / "job_state.json"))

    response = client.post("/jobs/123", json={"state": "interview", "notes": "Interview tomorrow morning"})
    assert response.status_code == 200

    json_data = load_state()
    assert "123" in json_data
    assert json_data["123"]["state"] == "interview"
    assert json_data["123"]["notes"] == "Interview tomorrow morning"


def test_offer_job(tmp_path, monkeypatch):
    monkeypatch.setenv("STATE_FILE", str(tmp_path / "job_state.json"))

    response = client.post("/jobs/123", json={"state": "offer", "notes": "Offered lots of money"})
    assert response.status_code == 200

    json_data = load_state()
    assert "123" in json_data
    assert json_data["123"]["state"] == "offer"
    assert json_data["123"]["notes"] == "Offered lots of money"
