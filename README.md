# Duunihaku — Daily Job Listings Dashboard

> A small Python tool that filters job listings from [TheirStack](https://theirstack.com) to make up for LinkedIn’s limited search capabilities.

![Sucks](./assets/sucks.gif)

> Perhaps a kanban integration in the future, since I'm currently tracking my job applications manually.

---

## Overview

LinkedIn’s job search filters are often too restrictive.
These scripts use the **TheirStack API** to fetch and filter jobs for me.

---

## Features

- Fetch **Finnish (FI)** and **EMEA remote jobs** using TheirStack API.
- Filter jobs by:
  - Keywords in **title** or **description** (e.g., Kubernetes, Cassandra, Linux)
  - **Location** (onsite jobs within 50km of Jyväskylä)
  - **Remote / hybrid jobs**
  - **English-only** job descriptions
  - Dealbreaker phrases (e.g., "must be UK based", "German only")
- Timestamped job listings for daily tracking.
- **Streamlit dashboard** for:
  - Browsing jobs
  - Searching by title, company, or location
  - Marking jobs as **applied**
  - Viewing applied jobs
- **Docker-ready setup** with cronjob to fetch jobs daily.

---

## Getting Started

1. Clone the repo
2. pip install -r requirements.txt
3. Set up environment variables in .env:
4. Run runner.sh to create the .json files.
5. Run the UI with "streamlit run viewer2.py"

---

## Docker usage (still janky)

1. docker build -t duunihaku .
2. docker run -p 8501:8501 -v $(pwd)/jaysons:/app/jaysons duunihaku:latest &
