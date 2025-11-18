from fastapi.testclient import TestClient
from api.main import app
from api.store import load_state

client = TestClient(app)


def test_update_notes():
    # Ensure initial state exists
    client.post("/jobs/777", json={"state": "saved", "notes": "before"})

    # Patch notes
    res = client.patch("/jobs/777/notes", json={"notes": "updated note"})
    assert res.status_code == 200

    body = res.json()
    assert body["notes"] == "updated note"
    assert body["state"] == "saved"  # unchanged

    stored = load_state()
    assert stored["777"]["notes"] == "updated note"
