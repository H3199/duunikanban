#!/usr/bin/env python3
import json
import os
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Job Listings Viewer", layout="wide")
st.title("Daily Job Listings Dashboard")

DATA_DIR = "jaysons"
FI_PREFIX = "fi_"
EMEA_PREFIX = "emea_"
LATEST_SUFFIX = "_latest.json"


def find_available_dates(prefix):
    """Return sorted list of available YYYY-MM-DD dates for a given file prefix."""
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
        return {}
    try:
        with open(file_path) as f:
            data = json.load(f)
        if raw:
            return data  # return full JSON including fetched_at
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return data
    except Exception as e:
        st.error(f"Error loading {file_path}: {e}")
        return {}


def render_jobs(jobs):
    """Render job listings nicely."""
    count = 0
    for job in jobs:
        title = job.get("job_title", "")
        company = job.get("company", "")
        location = job.get("country", "")
        desc = job.get("description", "")
        if (
            query in title.lower()
            or query in company.lower()
            or query in location.lower()
        ):
            with st.container():
                st.markdown(f"### [{title}]({job.get('url', '')})")
                st.write(f"**Company:** {company}")
                st.write(f"**Location:** {location}")
                if "distance_from_home_km" in job:
                    st.caption(f" {job['distance_from_home_km']} km from home")
                if desc:
                    st.caption(job.get("description", "")[:10000] + "...")
                st.divider()
                count += 1
    if count == 0:
        st.info("No matching results found.")


# --- Select date ---
available_fi_dates = find_available_dates(FI_PREFIX)
available_emea_dates = find_available_dates(EMEA_PREFIX)

# --- Select date ---
available_fi_dates = find_available_dates(FI_PREFIX)
available_emea_dates = find_available_dates(EMEA_PREFIX)

# Default to latest available date
latest_date = available_fi_dates[0] if available_fi_dates else datetime.now().strftime("%Y-%m-%d")
selected_date = st.sidebar.selectbox("Select date", available_fi_dates or [latest_date])

# Check for "_latest.json" fallback
fi_latest_path = os.path.join(DATA_DIR, f"{FI_PREFIX}latest.json")
emea_latest_path = os.path.join(DATA_DIR, f"{EMEA_PREFIX}latest.json")

# Use _latest.json if it exists and selected_date == latest_date
if os.path.exists(fi_latest_path) and selected_date == latest_date:
    FI_FILE = fi_latest_path
else:
    FI_FILE = os.path.join(DATA_DIR, f"{FI_PREFIX}{selected_date}.json")

if os.path.exists(emea_latest_path) and selected_date == latest_date:
    EMEA_FILE = emea_latest_path
else:
    EMEA_FILE = os.path.join(DATA_DIR, f"{EMEA_PREFIX}{selected_date}.json")

jobs_fi = load_jobs(FI_FILE)
jobs_emea = load_jobs(EMEA_FILE)

# --- Shared search box ---
query = st.text_input("🔍 Search (title, company, or location):", "").strip().lower()

# --- Tabs ---
tab_fi, tab_emea = st.tabs(["🇫🇮 Jobs", "🇪🇺 Remote Jobs"])

# Extract timestamps if available
timestamp_fi = jobs_fi_meta.get("fetched_at", "Unknown") if isinstance(jobs_fi_meta := load_jobs(FI_FILE, raw=True), dict) else "Unknown"
timestamp_emea = jobs_emea_meta.get("fetched_at", "Unknown") if isinstance(jobs_emea_meta := load_jobs(EMEA_FILE, raw=True), dict) else "Unknown"

# --- Display ---
with tab_fi:
    st.subheader(f"🇫🇮 Jobs ({len(jobs_fi)}) — fetched {timestamp_fi}")
    render_jobs(jobs_fi)

with tab_emea:
    st.subheader(f"🇪🇺 Remote Jobs ({len(jobs_emea)}) — fetched {timestamp_emea}")
    render_jobs(jobs_emea)
