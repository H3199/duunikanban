# test/unit/test_state_change.py
import pytest
#from state_manager import update_job_state, apply_state_to_jobs
from mytypes import JobRecord
from myclasses import Job
from job_state import JobState


def test_job_state_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("STATE_FILE", str(tmp_path / "state.json"))

    job = Job(id=123, title="DevOps", company="Test", url="x", description="")
    job.update_state(JobState.SAVED, "Cool job")

    # simulate reload
    jobs = Job.apply_saved_state([job])

    assert jobs[0].state == JobState.SAVED
    assert jobs[0].notes == "Cool job"
