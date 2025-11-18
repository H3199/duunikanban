from fastapi import FastAPI, HTTPException, Body
from .services import update_job_state, apply_state_to_jobs, persist_job, update_notes
from .store import load_state
from myclasses import JobState, Job
from pydantic import BaseModel

app = FastAPI(title="Duunihaku API")


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


# Return all jobs currently tracked in job_state.json.
@app.get("/jobs")
def list_jobs():

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
