from datetime import datetime

from models.schema import Job, JobRegion, JobState, JobStateHistory
from sqlmodel import Session


def test_get_jobs_returns_list(client):
    r = client.get("/api/v1/jobs")
    assert r.status_code == 200

    jobs = r.json()
    assert isinstance(jobs, list)
    assert len(jobs) > 5

    # verify one specific known job is present
    titles = {j["title"] for j in jobs}
    assert "Site Reliability Engineer" in titles


def test_db_schema_is_valid(test_engine):
    from sqlmodel import SQLModel, inspect

    inspector = inspect(test_engine)

    assert "job" in inspector.get_table_names()
    assert "jobstatehistory" in inspector.get_table_names()
    assert "user" in inspector.get_table_names()


def test_update_job_state(client):
    jobs = client.get("/api/v1/jobs").json()
    job_id = jobs[0]["id"]

    r = client.post(f"/api/v1/jobs/{job_id}/state", json={"state": "saved"})
    assert r.status_code == 200
    assert r.json()["state"] == "saved"

    job = client.get(f"/api/v1/jobs/{job_id}").json()
    assert job["state"] == "saved"

    r = client.post(f"/api/v1/jobs/{job_id}/state", json={"state": "trash"})
    assert r.status_code == 200
    assert r.json()["state"] == "trash"

    job = client.get(f"/api/v1/jobs/{job_id}").json()
    assert job["state"] == "trash"


def test_update_notes(client):
    jobs = client.get("/api/v1/jobs").json()
    job_id = jobs[0]["id"]

    r = client.patch(f"/api/v1/jobs/{job_id}/notes", json={"notes": "foo"})
    assert r.status_code == 200

    job = client.get(f"/api/v1/jobs/{job_id}").json()
    assert job["notes"] == "foo"

    r = client.patch(f"/api/v1/jobs/{job_id}/notes", json={"notes": "bar"})
    assert r.status_code == 200

    job = client.get(f"/api/v1/jobs/{job_id}").json()
    assert job["notes"] == "bar"


def test_ordering_by_updated_at(client):
    jobs = client.get("/api/v1/jobs").json()
    timestamps = [j["updated_at"] for j in jobs if j["updated_at"] is not None]
    assert timestamps == sorted(timestamps, reverse=True)


def test_create_and_get_job(client):
    # Step 1: POST - create a new job
    payload = {
        "title": "Test Job Create",
        "company": "Test Company",
        "url": "https://example.com/job/123",
        "description": "This is a test job",
        "country": "FI",
        "latitude": 60.1699,
        "longitude": 24.9384,
        "remote": True,
        "hybrid": False,
        "region": JobRegion.FI.value,
        "initial_state": JobState.SAVED.value,
        "notes": "Initial notes for test job",
    }

    r = client.post("/api/v1/jobs", json=payload)
    assert r.status_code == 200

    job_data = r.json()
    print(job_data)
    job_id = job_data["id"]

    # Verify POST response
    assert job_data["title"] == payload["title"]
    assert job_data["company"] == payload["company"]
    assert job_data["region"] == payload["region"]
    assert job_data["state"] == payload["initial_state"]
    assert job_data["notes"] == payload["notes"]

    # Step 2: GET - retrieve the job from the API
    r2 = client.get(f"/api/v1/jobs/{job_id}")
    assert r2.status_code == 200

    retrieved = r2.json()
    assert retrieved["title"] == payload["title"]
    assert retrieved["company"] == payload["company"]
    assert retrieved["region"] == payload["region"]
    assert retrieved["state"] == payload["initial_state"]
    assert retrieved["notes"] == payload["notes"]
