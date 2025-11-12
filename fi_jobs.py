#!/usr/bin/env python3
import requests
import logging
import json
import os
from dotenv import load_dotenv
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime

load_dotenv()

theirstack_key = os.getenv("THEIRSTACK_API_KEY")
home_lat = float(os.getenv("HOME_LAT"))
home_lon = float(os.getenv("HOME_LON"))
#openai_key = os.getenv("OPENAI_API_KEY")

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),  # set LOG_LEVEL=DEBUG in .env to enable debug dump
    format="%(asctime)s [%(levelname)s] %(message)s",
)


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
        logging.info("Fetched Finnish jobs successfully.")
        return response.json()
    else:
        logging.error(f"API error {response.status_code}: {response.text}")
        return {"data": []}


# This function filters out onsite jobs outside the defined radius of home coordinates.
def filter_jobs(jobs, radius_km=50):
    filtered = []
    for job in jobs:
        remote = job.get("remote", False)
        hybrid = job.get("hybrid", False)
        lat = job.get("latitude")
        lon = job.get("longitude")
        desc = job.get("job_description", "").lower()

        # Check description for remote/hybrid hints if flags are not set
        if not remote and not hybrid:
            if any(word in desc for word in ["remote", "hybrid","hybridi", "hybridimahdollisuus", "joustava", "etätyö", "etänä", "etätyönä", "etätyömahdollisuus"]):
                remote = True

        if remote or hybrid:
            # Always include remote/hybrid
            job["filter_reason"] = "remote_or_hybrid"
            filtered.append(job)
        elif lat is not None and lon is not None:
            distance = haversine(home_lat, home_lon, lat, lon)
            if distance <= radius_km:
                job["distance_from_home_km"] = round(distance, 2)
                job["filter_reason"] = f"onsite_within_{radius_km}km"
                filtered.append(job)

    return filtered


# This function calculates the distance between two coordinate points
def haversine(lat1 : float, lon1 : float, lat2 : float, lon2 : float):
    R = 6371.0  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


if __name__ == "__main__":
    jobs_FI = fetch_jobs_FI()

    if isinstance(jobs_FI, dict) and "data" in jobs_FI:
        jobs_list = jobs_FI["data"]
    else:
        jobs_list = jobs_FI

    logging.info(f"Fetched {len(jobs_list)} jobs before filtering.")
    filtered_jobs = filter_jobs(jobs_list)
    logging.info(f"{len(filtered_jobs)} jobs remained after filtering.")

    # If in DEBUG mode, dump unfiltered jobs for inspection
    if logging.getLogger().level == logging.DEBUG:
        debug_file = "debug_fi_jobs.json"
        with open(debug_file, "w") as f:
            json.dump(jobs_list, f, indent=2)
        logging.debug(f"Dumped unfiltered job data to {debug_file}")

    output = {
        "fetched_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "data": filtered_jobs,
    }

    print(json.dumps(output, indent=2))
