from fastapi import APIRouter, HTTPException, Body, Query
from uuid import UUID
from sqlmodel import Session, select, desc, asc
from core.database import engine
from models.schema import Job, JobStateHistory, JobState
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter(prefix="/jobs", tags=["Jobs"])

RANGE_MAP = {
    "12h": timedelta(hours=12),
    "24h": timedelta(hours=24),
    "48h": timedelta(hours=48),
    "7d": timedelta(days=7),
}


def normalize_ts(v):
    if not v:
        return None
    if isinstance(v, datetime):
        return v
    # assume string
    try:
        return datetime.fromisoformat(v)
    except:
        # last-chance fallback for older timestamps
        return datetime.strptime(v.split(".")[0], "%Y-%m-%d %H:%M:%S")


@router.get("")
def list_jobs(range: str | None = Query(None)):

    cutoff = None
    if range and range in RANGE_MAP:
        cutoff = datetime.utcnow() - RANGE_MAP[range]

    with Session(engine) as session:
        stmt = (
            select(Job)
            .outerjoin(JobStateHistory)
            .order_by(desc(JobStateHistory.timestamp))
        )
        jobs = session.exec(stmt).unique().all()

        formatted = []
        for job in jobs:
            latest = job.history[-1] if job.history else None
            state = latest.state if latest else "new"
            updated_at = normalize_ts(latest.timestamp if latest else None)

            if cutoff and state == "new":
                if not updated_at or updated_at < cutoff:
                    continue

            formatted.append(
                {
                    **job.dict(),
                    "state": state,
                    "notes": latest.notes if latest else "",
                    "updated_at": updated_at.isoformat() if updated_at else None,
                }
            )

        formatted.sort(key=lambda j: normalize_ts(j["updated_at"]) or datetime.min, reverse=True)

        return formatted



@router.get("/{job_id}")
def get_job(job_id: UUID):
    with Session(engine) as session:
        job = session.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Fetch latest state entry
        latest_entry = session.exec(
            select(JobStateHistory)
            .where(JobStateHistory.job_id == job_id)
            .order_by(desc(JobStateHistory.timestamp))
        ).first()

        # Fetch first time it was marked applied
        applied_entry = session.exec(
            select(JobStateHistory)
            .where(JobStateHistory.job_id == job_id)
            .where(JobStateHistory.state == "applied")
            .order_by(asc(JobStateHistory.timestamp))
        ).first()

        response = job.dict()

        response["state"] = latest_entry.state if latest_entry else "new"
        response["notes"] = latest_entry.notes if latest_entry else ""
        response["updated_at"] = latest_entry.timestamp if latest_entry else None
        response["applied_at"] = applied_entry.timestamp if applied_entry else None

        return response


class JobUpdate(BaseModel):
    state: JobState | None = None
    notes: str | None = None


@router.post("/{job_id}/state")
def update_job_state(job_id: UUID, payload: JobUpdate):
    with Session(engine) as session:
        job = session.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Determine previous notes if none provided
        last_notes = job.history[-1].notes if job.history else ""

        history = JobStateHistory(
            job_id=job_id,
            user_id=None,
            state=payload.state or JobState.NEW,
            notes=payload.notes if payload.notes is not None else last_notes
        )

        session.add(history)
        session.commit()
        session.refresh(history)

        return {
            "job_id": job_id,
            "state": history.state,
            "notes": history.notes
        }


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
