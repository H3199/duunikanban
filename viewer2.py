#!/usr/bin/env python3
import json
import os
import streamlit as st
from datetime import datetime

# Config
st.set_page_config(page_title="Job Listings Viewer", page_icon="assets/Tonninseteli.png" , layout="wide")
st.title("Daily Job Listings Dashboard")

DATA_DIR = "jaysons"
FI_PREFIX = "fi_"
EMEA_PREFIX = "emea_"
APPLIED_FILE = os.path.join(DATA_DIR, "applied_jobs.json")
LATEST_SUFFIX = "_latest.json"

# Return sorted list of available YYYY-MM-DD dates for a given file prefix.
def find_available_dates(prefix):
    dates = []
    for filename in os.listdir(DATA_DIR):
        if filename.startswith(prefix) and filename.endswith(".json") and "_latest" not in filename:
            try:
                date_str = filename.removeprefix(prefix).removesuffix(".json")
                datetime.fromisoformat(date_str)
                dates.append(date_str)
            except Exception:
                pass
    return sorted(dates, reverse=True)


def load_jobs(file_path, raw=False):
    if not os.path.exists(file_path):
        st.warning(f"File not found: `{file_path}`")
        return {} if raw else []
    try:
        with open(file_path) as f:
            data = json.load(f)
        if raw:
            return data
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return data
    except Exception as e:
        st.error(f"Error loading {file_path}: {e}")
        return {} if raw else []


def save_jobs(jobs, file_path):
    """Persist job list as JSON."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        json.dump({"data": jobs}, f, indent=2)


# Job rendering
def render_jobs(jobs, query=""):
    count = 0
    for job in jobs:
        title = job.get("job_title", "")
        company = job.get("company", "")
        location = job.get("country", "")
        desc = job.get("description", "")

        if query and query not in (title+company+location).lower():
            continue

        with st.container():
            st.markdown(f"### [{title}]({job.get('url','')})")
            st.write(f"**Company:** {company}")
            st.write(f"**Location:** {location}")
            if "distance_from_jyvaskyla_km" in job:
                st.caption(f"📍 {job['distance_from_jyvaskyla_km']} km from Jyväskylä")
            if desc:
                st.caption(desc[:10000] + "...")
            st.divider()
            count += 1
    if count == 0:
        st.info("No matching results found.")


def render_jobs_with_apply(jobs, source_file, query=""):
    """Render jobs with 'Mark as applied' checkbox and persist applied jobs."""
    updated_jobs = jobs.copy()
    applied_jobs = load_jobs(APPLIED_FILE)

    for job in jobs:
        title = job.get("job_title", "")
        company = job.get("company", "")
        location = job.get("country", "")
        desc = job.get("description", "")

        if query and query not in (title+company+location).lower():
            continue

        with st.container():
            st.markdown(f"### [{title}]({job.get('url','')})")
            st.write(f"**Company:** {company}")
            st.write(f"**Location:** {location}")
            if "distance_from_home_km" in job:
                st.caption(f"📍 {job['distance_from_home_km']} km from home")
            if desc:
                st.caption(desc[:10000]+"...")

            # Checkbox for applied
            applied = st.checkbox("Mark as applied", key=f"{source_file}_{job.get('id')}")
            if applied:
                applied_jobs.append(job)
                save_jobs(applied_jobs, APPLIED_FILE)
                updated_jobs = [j for j in updated_jobs if j.get("id") != job.get("id")]

    # Save the updated source JSON to persist removal of applied jobs
    save_jobs(updated_jobs, source_file)
    return updated_jobs

# Sidebar: select date
available_fi_dates = find_available_dates(FI_PREFIX)
available_emea_dates = find_available_dates(EMEA_PREFIX)
latest_date = available_fi_dates[0] if available_fi_dates else datetime.now().strftime("%Y-%m-%d")
selected_date = st.sidebar.selectbox("Select date", available_fi_dates or [latest_date])

# Compose file paths
FI_FILE = os.path.join(DATA_DIR, f"{FI_PREFIX}{selected_date}.json")
EMEA_FILE = os.path.join(DATA_DIR, f"{EMEA_PREFIX}{selected_date}.json")

jobs_fi = load_jobs(FI_FILE)
jobs_emea = load_jobs(EMEA_FILE)

# Shared search box
query = st.text_input("🔍 Search (title, company, or location):", "").strip().lower()

# Extract timestamps
timestamp_fi = load_jobs(FI_FILE, raw=True).get("fetched_at", "Unknown")
timestamp_emea = load_jobs(EMEA_FILE, raw=True).get("fetched_at", "Unknown")

# Tabs
tab_fi, tab_emea, tab_applied = st.tabs(["🇫🇮 Jobs", "🇪🇺 Remote Jobs", "✅ Applied Jobs"])

with tab_fi:
    st.subheader(f"🇫🇮 Jobs ({len(jobs_fi)}) — fetched {timestamp_fi}")
    jobs_fi = render_jobs_with_apply(jobs_fi, FI_FILE, query=query)

with tab_emea:
    st.subheader(f"🇪🇺 Remote Jobs ({len(jobs_emea)}) — fetched {timestamp_emea}")
    jobs_emea = render_jobs_with_apply(jobs_emea, EMEA_FILE, query=query)

with tab_applied:
    applied_jobs = load_jobs(APPLIED_FILE)
    st.subheader(f"✅ Applied Jobs ({len(applied_jobs)})")
    render_jobs(applied_jobs, query=query)
