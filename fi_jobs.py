#!/usr/bin/env python3
import requests
import json
import os
from dotenv import load_dotenv
from math import radians, sin, cos, sqrt, atan2

load_dotenv()

theirstack_key = os.getenv("THEIRSTACK_API_KEY")
jkl_lat = 62.2426
jkl_lon = 25.7473
#openai_key = os.getenv("OPENAI_API_KEY")


def fetch_jobs_FI():
    url = "https://api.theirstack.com/v1/jobs/search"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {theirstack_key}"
        }
    data = {
        "page": 0,
        "limit": 25,
        "job_country_code_or": ["FI"],
        "posted_at_max_age_days": 1,
        "job_description_pattern_or": ["devops", "kubernetes", "cassandra", "linux"],
        "job_title_or": ["devops", "site reliability", "infrastructure", "platform", "system", "administrator", "dba"]
        }
    response = requests.post(url, headers=headers, json=data)
    if response.ok:
        return response.json()
    else:
        return ("Error:", response.status_code, response.text)

def filter_jobs(jobs, radius_km=50):
    filtered = []
    for job in jobs:
        remote = job.get("remote", False)
        hybrid = job.get("hybrid", False)
        lat = job.get("latitude")
        lon = job.get("longitude")

        if remote or hybrid:
            # Always include remote/hybrid
            job["filter_reason"] = "remote_or_hybrid"
            filtered.append(job)
        elif lat is not None and lon is not None:
            # Include onsite jobs near Jyväskylä
            distance = haversine(jkl_lat, jkl_lon, lat, lon)
            if distance <= radius_km:
                job["distance_from_jyvaskyla_km"] = round(distance, 2)
                job["filter_reason"] = f"onsite_within_{radius_km}km"
                filtered.append(job)

    return filtered

# This function calculates the distance between two coordinate points
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def filter_jobs_near_jkl(jobs, radius_km=50):
    filtered = []
    for job in jobs:
        lat = job.get("latitude")
        lon = job.get("longitude")
        if lat is not None and lon is not None:
            distance = haversine(jkl_lat, jkl_lon, lat, lon)
            if distance <= radius_km:
                job["distance_from_jyvaskyla_km"] = round(distance, 2)
                filtered.append(job)
    return filtered


def filter_remote_jobs(jobs, include=True):
    filtered = []
    for job in jobs:
        remote = job.get("remote", False)
        hybrid = job.get("hybrid", False)

        if include:
            if remote or hybrid:
                filtered.append(job)
        else:
            if not remote and not hybrid:
                filtered.append(job)

    return filtered

if __name__ == "__main__":
    jobs_FI = fetch_jobs_FI()

    # Extract the job list
    if isinstance(jobs_FI, dict) and "data" in jobs_FI:
        jobs_list = jobs_FI["data"]
    else:
        jobs_list = jobs_FI

    filtered_jobs = filter_jobs(jobs_list)

    print(json.dumps(filtered_jobs, indent=2))
