#!/usr/bin/env python3
import random
import time
import requests
import json
from bs4 import BeautifulSoup
from typing import List, Dict, Optional

USER_AGENT = "DuunikanbanBot/1.0 (contact: eerohaavisto@gmail.com)"

BASE_SEARCH_URL = "https://www.itewiki.fi/search_results/posts"
BASE_DOMAIN = "https://www.itewiki.fi"

DEFAULT_PARAMS = {
    "formType": "job_search",
    "sorting": "job",
    "isActive": "1",
    "pageSize": "50",
    "page": "1",
}

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})


def polite_wait():
    time.sleep(random.uniform(0.5, 1.5))


# Fetch listing page and extract job detail URLs.
def get_job_urls(page: int = 1) -> List[str]:

    params = DEFAULT_PARAMS.copy()
    params["page"] = str(page)

    resp = session.get(BASE_SEARCH_URL, params=params)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # refine selector later if needed
    urls = []
    for a in soup.select("a[href*='rekryilmoitus']"):
        href = a.get("href")
        if href and href.startswith("/"):
            urls.append(BASE_DOMAIN + href)

    return list(set(urls))  # remove dupes


# Extract first JSON-LD JobPosting block.
def extract_json_ld(html: str) -> Optional[dict]:
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", {"type": "application/ld+json"})
    if not script:
        return None

    try:
        data = json.loads(script.string)
    except Exception:
        return None

    # sometimes schema is wrapped in a list
    if isinstance(data, list):
        data = data[0]

    if data.get("@type") != "JobPosting":
        return None

    return data

# Scrape single job from detail page.
def scrape_job(url: str) -> Optional[Dict]:
    polite_wait()
    resp = session.get(url)
    resp.raise_for_status()

    data = extract_json_ld(resp.text)
    if not data:
        return None

    return {
        "source": "itewiki",
        "id": hash(url),
        "url": data.get("url") or url,
        "job_title": data.get("title"),
        "company": data.get("hiringOrganization", {}).get("name"),
        "description": data.get("description"),
        "date_posted": data.get("datePosted"),
        "valid_through": data.get("validThrough"),
        "country": data.get("jobLocation", {}).get("address", {}).get("addressCountry"),
        "logo": data.get("hiringOrganization", {}).get("logo"),
        "employment_type": data.get("employmentType"),
    }


# Scrape multiple pages and return list of job dicts.
def scrape_all(pages: int = 3) -> List[Dict]:

    all_jobs = []
    seen_urls = set()

    for page in range(1, pages + 1):
    #    print(f"Fetching page {page}...")
        urls = get_job_urls(page)

        for url in urls:
            if url in seen_urls:
                continue
            seen_urls.add(url)

        #    print(f" → Scraping job: {url}")
            job = scrape_job(url)
            if job:
                all_jobs.append(job)

    return all_jobs


if __name__ == "__main__":
#    print("Starting ITEwiki scrape...")
    results = scrape_all(pages=5)  # adjustable
#    print(f"\nDone. Found {len(results)} jobs.")
    print(json.dumps(results, indent=2, ensure_ascii=False))
