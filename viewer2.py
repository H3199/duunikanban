import json
import os
import logging
import streamlit as st
from myclasses import Job, JobState
from datetime import datetime

# Config
st.set_page_config(page_title="Job Listings Viewer", page_icon="assets/Tonninseteli.png" , layout="wide")
st.title("Daily Job Listings Dashboard")

DATA_DIR = "jaysons"
FI_PREFIX = "fi_"
EMEA_PREFIX = "emea_"
APPLIED_FILE = os.path.join(DATA_DIR, "applied_jobs.json")
LATEST_SUFFIX = "_latest.json"

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(message)s",
)

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


def load_jobs(file_path: str) -> tuple[list[Job], str]:
    """
    Load jobs from JSON and always return (jobs_list, timestamp).
    Compatible with:
    - {"fetched_at": "...", "data": [...]}
    - legacy format: [...]
    - empty/invalid files
    """
    if not os.path.exists(file_path):
        logging.warning(f"{file_path} does not exist.")
        return [], "Unknown"

    try:
        with open(file_path, "r") as f:
            raw = f.read().strip()

        # Empty file → return empty state
        if not raw:
            logging.warning(f"{file_path} was empty.")
            return [], "Unknown"

        data = json.loads(raw)

    except json.JSONDecodeError:
        logging.error(f"{file_path} contains invalid JSON.")
        return [], "Unknown"
    except Exception as e:
        logging.error(f"Unexpected error loading {file_path}: {e}")
        return [], "Error"

    # New format
    if isinstance(data, dict):
        timestamp = data.get("fetched_at", "Unknown")
        records = data.get("data", [])
    else:
        # Legacy list-only format
        timestamp = "Unknown"
        records = data

    jobs: list[Job] = []
    for record in records:
        if isinstance(record, dict) and "state" in record:
            jobs.append(Job.from_dict(record))
        else:
            jobs.append(Job.from_raw(record))

    return jobs, timestamp


def save_jobs(jobs, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    serializable = {"data": [job.to_dict() for job in jobs]}
    with open(file_path, "w") as f:
        json.dump(serializable, f, indent=2)


# Job rendering
def render_jobs(jobs, query=""):
    count = 0
    for job in jobs:
        title = job.title
        company = job.company
        location = job.country
        desc = job.description
        url = job.url
        distance = job.distance_from_home_km

        if query and query not in (title+company+location).lower():
            continue

        with st.container():
            st.markdown(f"### [{title}]({url})")
            st.write(f"**Company:** {company}")
            st.write(f"**Location:** {location}")
            if distance is not None:
                st.caption(f"{distance} km from home")
            if desc:
                st.caption(desc[:10000] + "...")
            st.divider()
            count += 1
    if count == 0:
        st.info("No matching results found.")


# Render jobs with 'Mark as applied' checkbox and persist applied jobs.
def render_jobs_with_apply(jobs: list[Job], source_file: str, query: str = "") -> list[Job]:
    # Incoming jobs for this list (FI/EMEA)
    updated_jobs = jobs.copy()

    # Load already-applied jobs
    applied_jobs, _ = load_jobs(APPLIED_FILE)
    applied_ids = {j.id for j in applied_jobs}

    changed = False

    for job in jobs:
        title = job.title
        company = job.company
        location = job.country
        desc = job.description
        url = job.url
        distance = job.distance_from_home_km

        # simple text filter
        if query and query not in (title + company + location).lower():
            continue

        with st.container():
            st.markdown(f"### [{title}]({url})")
            st.write(f"**Company:** {company}")
            st.write(f"**Location:** {location}")
            if distance is not None:
                st.caption(f"{distance} km from home")
            if desc:
                st.caption(desc[:10000] + "...")

            # Checkbox reflects whether this job is already applied
            applied = st.checkbox(
                "Mark as applied",
                key=f"{source_file}_{job.id}",
                value=(job.id in applied_ids),
            )

            # If user ticks it now and it wasn't applied before
            if applied and job.id not in applied_ids:
                applied_jobs.append(job)
                applied_ids.add(job.id)
                updated_jobs = [j for j in updated_jobs if j.id != job.id]
                changed = True

    # Only write to disk if something changed
    if changed:
        save_jobs(applied_jobs, APPLIED_FILE)
        save_jobs(updated_jobs, source_file)

    return updated_jobs


# Sidebar: select date
available_fi_dates = find_available_dates(FI_PREFIX)
available_emea_dates = find_available_dates(EMEA_PREFIX)
latest_date = available_fi_dates[0] if available_fi_dates else datetime.now().strftime("%Y-%m-%d")
selected_date = st.sidebar.selectbox("Select date", available_fi_dates or [latest_date])

# Compose file paths
logging.debug(f"Selected date: {selected_date}")
FI_FILE = os.path.join(DATA_DIR, f"{FI_PREFIX}{selected_date}.json")
EMEA_FILE = os.path.join(DATA_DIR, f"{EMEA_PREFIX}{selected_date}.json")

logging.debug(f"Loading jobs from {FI_FILE} and {EMEA_FILE}")
jobs_fi, timestamp_fi = load_jobs(FI_FILE)
jobs_emea, timestamp_emea = load_jobs(EMEA_FILE)

# Shared search box
query = st.text_input("🔍 Search (title, company, or location):", "").strip().lower()

# Tabs
tab_fi, tab_emea, tab_applied = st.tabs(["Finnish Jobs", "EMEA Remote Jobs", "Applied Jobs"])

with tab_fi:
    st.subheader(f"Finnish Jobs ({len(jobs_fi)}) — fetched {timestamp_fi}")
    jobs_fi = render_jobs_with_apply(jobs_fi, FI_FILE, query=query)


with tab_emea:
    st.subheader(f"EMEA Remote Jobs ({len(jobs_emea)}) — fetched {timestamp_emea}")
    jobs_emea = render_jobs_with_apply(jobs_emea, EMEA_FILE, query=query)

with tab_applied:
    applied_jobs, timestamp_applied = load_jobs(APPLIED_FILE)
    st.subheader(f"Applied Jobs ({len(applied_jobs)})")
    render_jobs(applied_jobs, query=query)
