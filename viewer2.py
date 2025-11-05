#!/usr/bin/env python3
import json
import os
import streamlit as st

st.set_page_config(page_title="Job Listings Viewer", layout="wide")
st.title("Daily Job Listings Dashboard")

FI_FILE = "jaysons/fi_latest.json"
EMEA_FILE = "jaysons/emea_latest.json"

def load_jobs(file_path):
    if not os.path.exists(file_path):
        st.warning(f"File not found: `{file_path}`")
        return []
    try:
        with open(file_path) as f:
            data = json.load(f)
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return data
    except Exception as e:
        st.error(f"Error loading {file_path}: {e}")
        return []

jobs_fi = load_jobs(FI_FILE)
jobs_emea = load_jobs(EMEA_FILE)

tab_fi, tab_emea = st.tabs(["🇫🇮 Jobs", "🇪🇺 Remote Jobs"])

# --- Shared search box ---
query = st.text_input("🔍 Search (title, company, or location):", "").strip().lower()

def render_jobs(jobs):
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
                if "distance_from_jyvaskyla_km" in job:
                    st.caption(f"📍 {job['distance_from_jyvaskyla_km']} km from Jyväskylä")
                if desc:
                    st.caption(job.get("description", "")[:10000] + "...")
                st.divider()
                count += 1
    if count == 0:
        st.info("No matching results found.")

# --- Finnish Jobs ---
with tab_fi:
    st.subheader(f"🇫🇮 Jobs ({len(jobs_fi)})")
    render_jobs(jobs_fi)

# --- EMEA Jobs ---
with tab_emea:
    st.subheader(f"🇪🇺 Remote Jobs ({len(jobs_emea)})")
    render_jobs(jobs_emea)
