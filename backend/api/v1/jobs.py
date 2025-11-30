from fastapi import APIRouter, HTTPException, Body
from uuid import UUID
from sqlmodel import Session, select, desc
from core.database import engine
from models.schema import Job, JobStateHistory, JobState
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("")
def list_jobs():
    with Session(engine) as session:
        # fetch jobs + joined history (latest first)
        statement = (
            select(Job)
            .outerjoin(JobStateHistory)
            .order_by(desc(JobStateHistory.timestamp))
        )
        jobs = session.exec(statement).unique().all()

        # Build response with computed state/updated_at
        formatted = [
            {
                **job.dict(),
                "state": job.history[-1].state if job.history else "new",
                "notes": job.history[-1].notes if job.history else "",
                "updated_at": job.history[-1].timestamp if job.history else None,
            }
            for job in jobs
        ]

        # Final sort: newest first using updated_at OR created_at fallback
        formatted.sort(
            key=lambda j: j["updated_at"] or datetime.min,
            reverse=True
        )
        return formatted



@router.get("/{job_id}")
def get_job(job_id: UUID):
    with Session(engine) as session:
        job = session.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Fetch latest state entry
        state_entry = session.exec(
            select(JobStateHistory)
            .where(JobStateHistory.job_id == job_id)
            .order_by(desc(JobStateHistory.timestamp))
        ).first()

        job_dict = job.dict()
        job_dict["state"] = state_entry.state if state_entry else "new"
        job_dict["notes"] = state_entry.notes if state_entry else ""

        return job_dict


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

        # Use existing state rather than defaulting to NEW
        current_state = job.history[-1].state if job.history else JobState.NEW

        history = JobStateHistory(
            job_id=job_id,
            user_id=None,
            state=current_state,
            notes=notes
        )
        session.add(history)
        session.commit()
        session.refresh(history)

        return {"job_id": job_id, "state": history.state, "notes": history.notes}
