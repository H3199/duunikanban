# tests/unit/test_emea_filter.py
import pytest
import json
import mytypes
from emea_jobs import filter_english_jobs

mock_data_file = "jaysons/mock_data/emea_sample.json"

with open(mock_data_file, "r") as f:
    mock_data = json.load(f)

def test_includes_english_jobs():
    jobs = [
        {"job_title": "Engineer", "description": "This is an English job", "remote": False, "hybrid": False, "latitude": 0, "longitude": 0},
        {"job_title": "French Job", "description": "Ceci est un emploi en français", "remote": False, "hybrid": False, "latitude": 0, "longitude": 0},
    ]

    result = filter_english_jobs(jobs)
    titles = [job["job_title"] for job in result]
    assert "Engineer" in titles
    assert "French Job" not in titles

def test_with_mock_data():
    jobs = mock_data
    raw_titles = [job["job_title"] for job in jobs]
    print("unfiltered")
    assert (len(raw_titles)) == 25
    for raw_title in raw_titles:
        print(raw_title)
    result = filter_english_jobs(jobs)
    titles = [job["job_title"] for job in result]
    print("filtered")
    assert len(titles) == 20
    for title in titles:
        print(title)
