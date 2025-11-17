from fastapi import FastAPI, HTTPException
from .services import update_job_state, apply_state_to_jobs, persist_job
from .store import load_state
from myclasses import JobState, Job
from pydantic import BaseModel

app = FastAPI(title="Duunihaku API")


class JobUpdate(BaseModel):
    state: JobState
    notes: str | None = None


@app.get("/state")
def get_state():
    return load_state()


@app.post("/jobs/{job_id}")
def set_job_state(job_id: int, update: JobUpdate):
    # No job repository yet: API is dumb, test provides job object
    updated = persist_job(job_id, update.state, update.notes)
    return {"id": job_id, **updated}


@app.get("/jobs")
def list_jobs():
    """
    Return all jobs currently tracked in job_state.json.
    Since we don’t yet pull from live JSON, this represents the "known" jobs.
    """

    data = load_state()

    # Convert stored state objects into response format
    response = []
    for job_id, record in data.items():
        response.append({
            "id": int(job_id),
            "state": record["state"],
            "notes": record.get("notes", "")
        })

    return response
