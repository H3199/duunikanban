from pydantic import BaseModel
from typing import Optional
from myclasses import JobState

class JobUpdate(BaseModel):
    state: JobState
    notes: Optional[str] = None

class JobOut(BaseModel):
    id: int
    title: str
    company: str
    state: JobState
    notes: Optional[str]
    updated_at: Optional[str]
