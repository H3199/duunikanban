#!/usr/bin/env python3
import requests
import logging
import json
import os
from dotenv import load_dotenv
from langdetect import detect, DetectorFactory
from datetime import datetime
from mytypes import JobRecord # Basically ORMish stuff, some technical debt here, because I never planned this project to grow this complex.
from core.database import engine # DB stuff, obviously.
from models.schema import Job, JobRegion, JobStateHistory
from typing import List
from sqlmodel import Session, select
from api.status import get_credits
from config_loader import load_config


DetectorFactory.seed = 0
load_dotenv()
config = load_config()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(message)s",
)

THEIRSTACK_KEY = os.getenv("THEIRSTACK_API_KEY")
DEALBREAKERS = config["emea_filters"]["dealbreakers"]
COUNTRIES = config["emea_filters"]["countries"]
EMEA_QUERY = config["emea_query"]


# Fetch EMEA remote jobs from TheirStack API and return as a list of JobRecord objects.
def fetch_jobs_emea() -> List[JobRecord]:
    url = "https://api.theirstack.com/v1/jobs/search"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {THEIRSTACK_KEY}"
        }
    data = {
        **EMEA_QUERY,
        "job_country_code_or": COUNTRIES,
        "job_description_pattern_not": DEALBREAKERS,
    }
    response = requests.post(url, headers=headers, json=data)

    if not response.ok:
        raise RuntimeError(
            f"EMEA fetch failed: {response.status_code} {response.text}"
        )
    payload = response.json()
    jobs_raw = payload.get("data", [])
    jobs: List[JobRecord] = [JobRecord(**job) for job in jobs_raw]
    return jobs


def filter_english_jobs(jobs: List[JobRecord]) -> List[JobRecord]:
    english_jobs: List[JobRecord] = []
    for job in jobs:
        description = job.get("description", "")
        if not description:
            continue
        try:
            lang = detect(description)
            if lang == "en":
                english_jobs.append(job)
        except Exception:
            continue
    return english_jobs


def save_jobs_to_db(jobs: List[JobRecord]):
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

                # Only update changed fields
                for field, value in updates.items():
                    if getattr(existing, field) != value:
                        setattr(existing, field, value)
                        changed = True

                # Ensure region is set
                if existing.region is None:
                    existing.region = JobRegion.EMEA
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
                    region=JobRegion.EMEA,
                )
                session.add(job)
                session.flush()  # ensures job.id exists

                # Create initial state record
                history = JobStateHistory(
                    job_id=job.id,
                    state="new",
                    notes=None,
                    timestamp=datetime.utcnow(),
                )
                session.add(history)

                inserted += 1

        session.commit()

    logging.info(f"[EMEA] DB sync complete — inserted: {inserted}, updated: {updated}")



if __name__ == "__main__":
    jobs_list = fetch_jobs_emea()
    logging.info(f"Fetched {len(jobs_list)} jobs before filtering.")

    english = filter_english_jobs(jobs_list)
    logging.info(f"{len(english)} detected English.")

    save_jobs_to_db(english)

    logging.info("Job sync completed.")
