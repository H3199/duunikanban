from typing import List
from myclasses import Job, JobState
from .store import persist_job, load_state, save_state


def apply_state_to_jobs(jobs: List[Job]) -> List[Job]:
    state_data = load_state()

    for job in jobs:
        record = state_data.get(str(job.id))
        if record:
            job.state = JobState(record["state"])
            job.notes = record.get("notes", "")
    return jobs


def update_job_state(job: Job, new_state: JobState, notes: str | None = None):
    job.state = new_state
    if notes:
        job.notes = notes
    persist_job(job.id, new_state, job.notes)
    return job


def update_notes(job_id: int, notes: str):
    data = load_state()
    record = data.get(str(job_id), {})

    data[str(job_id)] = {
        "state": record.get("state", JobState.NEW.value),
        "notes": notes
    }

    save_state(data)

    return data[str(job_id)]
