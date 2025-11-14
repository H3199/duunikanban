#!/usr/bin/env python3
import requests
import logging
import json
import os
from dotenv import load_dotenv
from langdetect import detect, DetectorFactory
from datetime import datetime
from mytypes import Job
from typing import List


dealbreakers = [
    "unpaid",
    "internship",
    "must be uk based",
    "uk-based",
    "must be in the uk",
    "uk only",
    "must live in the uk",
    "candidates must be in the uk",
    "work in the UK",
    "based in london",
    "must be located in london",
    "must be located in germany",
    "german citizens only",
    "must be based in germany",
    "must be based in france",
    "france only",
    "must be based in spain",
    "spain only",
    "must be based in italy",
    "must be located in italy",
    "based in poland",
    "based in netherlands",
    "must be based in netherlands",
    "based in belgium",
    "onsite only",
    "on-site only",
    "must relocate",
    "relocation required",
    "must be within commuting distance",
    "office based",
    "not a remote role",
    "remote within germany",
    "remote within uk",
    "remote within ireland",
    "remote in france",
    "remote in spain",
    "remote in poland",
    "remote within switzerland",
    "remote within austria",
    "remote within italy",
    "remote within eu only",
    "not available outside",
    "not open to remote workers abroad",
    "eligible to work in germany only",
    "eligible to work in uk only",
    "eligible to work in france only",
    "eligible to work in spain only",
    "eligible to work in italy only",
    "hybrid working",
    "fluent in german",
    "native german speaker",
    "german language required",
    "must speak german",
    "excellent german skills",
    "proficient in german",
    "german speaking",
    "bilingual in german",
    "german native",
    "german level",
    "spanish level",
    "french level",
    "italian level",
    "russian",
    "on-site"
    ]

emea = [
    "DE",  # Germany
    "DK",  # Denmark
    "FI",  # Finland
    "SE",  # Sweden
    "NO",  # Norway
    "EE",  # Estonia
    "LV",  # Latvia
    "LT",  # Lithuania
    "NL",  # Netherlands
    "BE",  # Belgium
    "PL",  # Poland
    "CZ",  # Czech Republic
    "SK",  # Slovakia
    "HU",  # Hungary
    "AT",  # Austria
    "CH",  # Switzerland
    "IE",  # Ireland
    "GB",  # United Kingdom
    "FR",  # France
    "ES",  # Spain
    "PT",  # Portugal
    "IT",  # Italy
    "RO",  # Romania
    "BG",  # Bulgaria
    "HR",  # Croatia
    "SI",  # Slovenia
    ]

DetectorFactory.seed = 0
load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(message)s",
)

THEIRSTACK_KEY = os.getenv("THEIRSTACK_API_KEY")
#openai_key = os.getenv("OPENAI_API_KEY")

# Fetch EMEA remote jobs from TheirStack API and return as a list of Job objects.
def fetch_jobs_emea() -> List[Job]:
    url = "https://api.theirstack.com/v1/jobs/search"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {THEIRSTACK_KEY}"
        }
    data = {
        "page": 0,
        "limit": 25,
        "remote": True,
        "job_country_code_or": emea,
        "job_description_pattern_not": dealbreakers,
        "posted_at_max_age_days": 1,
        "job_description_pattern_or": ["devops", "kubernetes", "cassandra", "linux"],
        "job_title_or": ["devops", "site reliability", "infrastructure", "platform", "system", "administrator", "dba"]
        }
    response = requests.post(url, headers=headers, json=data)
    if not response.ok:
        raise RuntimeError(
            f"EMEA fetch failed: {response.status_code} {response.text}"
        )
    payload = response.json()
    jobs_raw = payload.get("data", [])
    jobs: List[Job] = [Job(**job) for job in jobs_raw]
    return jobs


def filter_english_jobs(jobs: List[Job]) -> List[Job]:
    english_jobs: List[Job] = []
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


if __name__ == "__main__":
    # Fetch and filter jobs
    jobs_list = fetch_jobs_emea()
    logging.info(f"Fetched {len(jobs_list)} jobs before filtering.")
    en_jobs = filter_english_jobs(jobs_list)
    logging.info(f"{len(filtered_english_jobs)} jobs remained after filtering.")

    # Dump unfiltered jobs in debug mode
    if logging.getLogger().level == logging.DEBUG:
        debug_file = "debug_en_jobs.json"
        with open(debug_file, "w") as f:
            json.dump(jobs_list, f, indent=2)
        logging.debug(f"Dumped unfiltered job data to {debug_file}")

    # Wrap results with timestamp
    output = {
        "fetched_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "data": [job.__dict__ if hasattr(job, "__dict__") else job for job in en_jobs],
    }
    print(json.dumps(output, indent=2))
