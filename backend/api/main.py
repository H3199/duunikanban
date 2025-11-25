from fastapi import FastAPI, HTTPException, Body
from fastapi.openapi.models import APIKey
from fastapi.routing import APIRoute
from .services import update_job_state, apply_state_to_jobs, persist_job, update_notes
from .store import load_state, load_raw_jobs, load_all_jobs
from myclasses import JobState, Job
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Duunihaku API")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JobUpdate(BaseModel):
    state: JobState | None = None
    notes: str | None = None


@app.get("/state")
def get_state():
    return load_state()


@app.post("/jobs/{job_id}")
def set_job_state(job_id: int, update: JobUpdate):
    # No job repository yet: API is dumb, test provides job object
    updated = persist_job(job_id, update.state, update.notes)
    return {"id": job_id, **updated}


@app.get("/jobs/{job_id}")
def get_job(job_id: int):
    jobs = load_all_jobs()

    job = next((j for j in jobs if j.id == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job.to_dict()


@app.get("/jobs")
def list_jobs():
    # 1) Load job feed (scraped or cached job list)
    jobs = load_raw_jobs()

    # 2) Load job state persistence
    saved_state = load_state()

    response = []

    for job in jobs:
        job_id_str = str(job.id)

        # If we have saved state, override fields
        if job_id_str in saved_state:
            job.state = saved_state[job_id_str].get("state", job.state)
            job.notes = saved_state[job_id_str].get("notes", job.notes)
            job.updated_at = saved_state[job_id_str].get("updated_at", job.updated_at)

        response.append(job.as_dict())

    return response


@app.post("/jobs/{job_id}/move/{new_state}")
def move_job(job_id: int, new_state: str):
    # Validate state
    try:
        state_enum = JobState(new_state)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid state: {new_state}")

    # Ensure job exists in saved state or initialize record
    saved = load_state()
    job_key = str(job_id)

    if job_key not in saved:
        # We allow "implicit create" on drag, but you can change this
        saved[job_key] = {"state": JobState.NEW.value, "notes": ""}

    # Persist new state
    updated = persist_job(job_id, state_enum, saved[job_key].get("notes", ""))

    return {
        "id": job_id,
        "state": updated["state"],
        "notes": updated.get("notes")
    }


@app.patch("/jobs/{job_id}/notes")
def patch_notes(job_id: int, notes: str = Body(..., embed=True)):
    return update_notes(job_id, notes)
