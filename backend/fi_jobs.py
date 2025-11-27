#!/usr/bin/env python3
import logging
import json
import os
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
from typing import List, Optional
import requests
from dotenv import load_dotenv
from mytypes import JobRecord
from sqlmodel import Session, select
from core.database import engine
from models.schema import Job, JobRegion, JobSource
from typing import List

load_dotenv()

THEIRSTACK_KEY = os.getenv("THEIRSTACK_API_KEY")
HOME_LAT = float(os.getenv("HOME_LAT"))
HOME_LON = float(os.getenv("HOME_LON"))

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def fetch_jobs_fi() -> List[JobRecord]:
    url = "https://api.theirstack.com/v1/jobs/search"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {THEIRSTACK_KEY}",
    }
    data = {
        "page": 0,
        "limit": 25,
        "job_country_code_or": ["FI"],
        "posted_at_max_age_days": 1,
        "job_description_pattern_or": [
            "devops", "kubernetes", "cassandra", "linux"
        ],
        "job_title_or": [
            "devops", "site reliability", "infrastructure", "platform",
            "system", "administrator", "dba"
        ],
    }
    response = requests.post(url, headers=headers, json=data)
    if not response.ok:
        raise RuntimeError(f"FI fetch failed: {response.status_code} {response.text}")

    return response.json().get("data", [])


def filter_jobs(jobs: List[JobRecord], radius_km: float = 50) -> List[JobRecord]:
    filtered: List[Job] = []
    for job in jobs:
        remote = job.get("remote", False)
        hybrid = job.get("hybrid", False)
        lat = job.get("latitude")
        lon = job.get("longitude")
        desc = job.get("job_description", "").lower()

        # Check description for remote/hybrid hints if flags are not set
        if not remote and not hybrid:
            if any(word in desc for word in [
                    "remote", "hybrid", "hybridi", "hybridimahdollisuus",
                    "joustava", "etätyö", "etänä", "etätyönä", "etätyömahdollisuus"
                ]
            ):
                remote = True

        if remote or hybrid:
            job["filter_reason"] = "remote_or_hybrid"
            filtered.append(job)
        elif lat is not None and lon is not None:
            distance = haversine(HOME_LAT, HOME_LON, lat, lon)
            if distance <= radius_km:
                job["distance_from_home_km"] = round(distance, 2)
                job["filter_reason"] = f"onsite_within_{radius_km}km"
                filtered.append(job)
    return filtered


#  This function calculates the distance between two coordinate points
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def save_jobs_to_db_fi(jobs: List[dict]):
    inserted = 0
    updated = 0

    with Session(engine) as session:
        for raw in jobs:

            external_id = str(raw["id"])

            existing = session.exec(
                select(Job).where(Job.external_id == external_id)
            ).first()

            if existing:
                changed = False

                updates = {
                    "title": raw["job_title"],
                    "company": raw["company"],
                    "url": raw["url"],
                    "description": raw.get("description", ""),
                    "country": raw.get("country", None),
                }

                for field, value in updates.items():
                    if getattr(existing, field) != value:
                        setattr(existing, field, value)
                        changed = True

                if existing.region is None:
                    existing.region = JobRegion.FI
                    changed = True

                if changed:
                    session.add(existing)
                    updated += 1

            else:
                job = Job(
                    external_id=external_id,
                    title=raw["job_title"],
                    company=raw["company"],
                    url=raw["url"],
                    description=raw.get("description", ""),
                    country=raw.get("country", None),
                    region=JobRegion.FI,
                )
                session.add(job)
                inserted += 1

        session.commit()

    logging.info(f"[FI] DB sync complete — inserted: {inserted}, updated: {updated}")


if __name__ == "__main__":
    jobs_list = fetch_jobs_fi()
    logging.info(f"(FI) Fetched {len(jobs_list)} jobs.")

    filtered = filter_jobs(jobs_list)
    logging.info(f"(FI) {len(filtered)} left after filtering.")

    # Optional debugging: write raw API response
    if logging.getLogger().level == logging.DEBUG:
        with open("debug_fi_jobs.json", "w") as f:
            json.dump(jobs_list, f, indent=2)
        logging.debug("Wrote debug_fi_jobs.json")

    save_jobs_to_db_fi(filtered)

    logging.info("(FI) Job sync completed.")
