from fastapi import APIRouter, HTTPException, Body
from uuid import UUID
from sqlmodel import Session, select
from backend.core.database import engine
from backend.models import Job, JobStateHistory, JobState

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("")
def list_jobs():
    with Session(engine) as session:
        jobs = session.exec(select(Job)).all()
        return [job.dict() for job in jobs]


@router.get("/{job_id}")
def get_job(job_id: UUID):
    with Session(engine) as session:
        job = session.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job.dict()


class JobUpdate(BaseModel):
    state: JobState | None = None
    notes: str | None = None


@router.post("/{job_id}/state")
def update_job_state(job_id: UUID, payload: JobUpdate):
    with Session(engine) as session:
        job = session.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Create state history record
        history = JobStateHistory(
            job_id=job_id,
            user_id=None,  # until auth exists
            state=payload.state or JobState.NEW,
            notes=payload.notes or ""
        )
        session.add(history)
        session.commit()
        session.refresh(history)

        return {"job_id": job_id, "state": history.state, "notes": history.notes}


@router.patch("/{job_id}/notes")
def update_notes(job_id: UUID, notes: str = Body(..., embed=True)):
    with Session(engine) as session:
        job = session.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        history = JobStateHistory(
            job_id=job_id,
            user_id=None,
            state=JobState.NEW,  # keeps previous state or set explicitly later
            notes=notes
        )
        session.add(history)
        session.commit()

        return {"job_id": job_id, "notes": notes}
