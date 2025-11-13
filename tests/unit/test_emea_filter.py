# tests/test_emea_filter.py
import pytest
from emea_jobs import filter_english_jobs

# Only thing we currently do in emea filter in Python is filter for english language.
# The rest we need to test with a mock JSON file.
# TODO: Add a mock JSON file and test the rest.


def test_includes_english_jobs():
    jobs = [
        {"job_title": "Engineer", "description": "This is an English job", "remote": False, "hybrid": False, "latitude": 0, "longitude": 0},
        {"job_title": "French Job", "description": "Ceci est un emploi en français", "remote": False, "hybrid": False, "latitude": 0, "longitude": 0},
    ]

    result = filter_english_jobs(jobs)
    titles = [job["job_title"] for job in result]
    assert "Engineer" in titles
    assert "French Job" not in titles
