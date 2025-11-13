# tests/test_filter_jobs.py
import pytest
import os
from dotenv import load_dotenv
from fi_jobs import filter_jobs

load_dotenv()

home_lat = float(os.getenv("HOME_LAT"))
home_lon = float(os.getenv("HOME_LON"))

def test_includes_remote_jobs():
    jobs = [
        {"job_title": "Remote", "remote": True, "latitude": None, "longitude": None},
        {"job_title": "Hybrid", "hybrid": True, "latitude": None, "longitude": None}
    ]

    result = filter_jobs(jobs)
    assert any(job["job_title"] == "Remote" for job in result)
    assert any(job["job_title"] == "Hybrid" for job in result)


def test_includes_onsite_near_home():
    jobs = [
        {"job_title": "Engineer", "latitude": home_lat, "longitude": home_lon}
    ]

    result = filter_jobs(jobs)
    assert any(job["job_title"] == "Engineer" for job in result)


def test_excludes_far_away_jobs():
    far_job = {"job_title": "Remote but not flagged", "latitude": 0.0, "longitude": 0.0}
    result = filter_jobs([far_job], radius_km=5)
    assert len(result) == 0


def test_includes_when_remote_or_hybrid_in_description_but_not_flagged():
    jobs = [
        {"job_title": "False flagged", "remote": False, "hybrid": False, "job_description": "Remote hybrid hybridi hybridimahdollisuus joustava etätyö etänä etätyönä etätyömahdollisuus"},
        {"job_title": "None flagged", "remote": None, "hybrid": None, "job_description": "Remote hybrid hybridi hybridimahdollisuus joustava etätyö etänä etätyönä etätyömahdollisuus"}
    ]

    result = filter_jobs(jobs)
    assert any(job["job_title"] == "False flagged" for job in result)
    assert any(job["job_title"] == "None flagged" for job in result)
