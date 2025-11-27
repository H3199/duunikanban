from sqlmodel import SQLModel, Field, Relationship, Column, String
from typing import Optional, List
from uuid import uuid4, UUID
from datetime import datetime
from enum import Enum



class JobRegion(str, Enum):
    FI = "fi"
    EMEA = "emea"
    UNSPECIFIED = "unspecified"


class JobState(str, Enum):
    NEW = "new"
    SAVED = "saved"
    APPLIED = "applied"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str
    password_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    job_states: List["JobStateHistory"] = Relationship(back_populates="user")


class JobSource(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    url: Optional[str] = None


class Job(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    external_id: Optional[str] = Field(default=None, index=True)
    title: str
    company: str
    url: str
    description: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    remote: Optional[bool] = False
    hybrid: Optional[bool] = False

    region: JobRegion = Field(default=JobRegion.UNSPECIFIED, index=True)

    source_id: Optional[int] = Field(default=None, foreign_key="jobsource.id")
    source: Optional[JobSource] = Relationship()

    history: List["JobStateHistory"] = Relationship(back_populates="job")


class CVVersion(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    version_label: str
    file_path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    history: List["JobStateHistory"] = Relationship(back_populates="cv_version")


class JobStateHistory(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    job_id: UUID = Field(foreign_key="job.id")
    user_id: Optional[UUID] = Field(default=None, foreign_key="user.id")
    cv_version_id: Optional[UUID] = Field(default=None, foreign_key="cvversion.id")

    state: JobState = Field(sa_column=Column(String, nullable=False))  # stored as text
    notes: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    job: Job = Relationship(back_populates="history")
    user: User = Relationship(back_populates="job_states")
    cv_version: Optional[CVVersion] = Relationship(back_populates="history")
