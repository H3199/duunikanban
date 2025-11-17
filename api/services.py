from typing import List
from myclasses import Job, JobState
from .store import persist_job, load_state

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
