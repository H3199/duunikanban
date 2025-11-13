#!/usr/bin/env python3
import requests
import json
import os
from dotenv import load_dotenv
from langdetect import detect, DetectorFactory
from datetime import datetime


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
    "remote within italy"
    "remote within eu only",
    "remote within switzerland",
    "remote within austria",
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

theirstack_key = os.getenv("THEIRSTACK_API_KEY")
#openai_key = os.getenv("OPENAI_API_KEY")


def fetch_jobs_emea():
    url = "https://api.theirstack.com/v1/jobs/search"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {theirstack_key}"
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
    if response.ok:
        return response.json()
    else:
        return ("Error:", response.status_code, response.text)


def filter_english_jobs(jobs):
    english_jobs = []
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
    jobs_emea = fetch_jobs_emea()

    if isinstance(jobs_emea, dict) and "data" in jobs_emea:
        jobs_list = jobs_emea["data"]
    else:
        jobs_list = jobs_emea
    en_jobs = filter_english_jobs(jobs_list)

# Wrap with a timestamp.
    output = {
    "fetched_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    "data": en_jobs
    }
    print(json.dumps(output))
