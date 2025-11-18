import json
import os
from myclasses import JobState

# TODO: are we pulling these from .env?
STATE_FILE = "jaysons/job_state.json"
DATA_DIR = "jaysons"


def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE) as f:
        return json.load(f)


def save_state(state: dict):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def persist_job(job_id: int, state: str | JobState, notes: str | None = None):
    data = load_state()

    # Normalize state: accept enum OR raw string
    if isinstance(state, str):
        state = JobState(state)

    record = data.get(str(job_id), {})

    data[str(job_id)] = {
        "state": state.value,
        "notes": notes if notes is not None else record.get("notes", "")
    }

    save_state(data)
    return data[str(job_id)]

# Load all jobs from fi_latest.json and emea_latest.json.
def load_raw_jobs():
    jobs = []

    for fname in ["fi_latest.json", "emea_latest.json"]:
        path = os.path.join(DATA_DIR, fname)
        if not os.path.exists(path):
            continue

        with open(path) as f:
            raw = json.load(f)

        for record in raw.get("data", []):
            jobs.append(Job.from_raw(record))

    return jobs
