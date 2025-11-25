#!/bin/bash
set -e

# Run jobs initially
/app/runner.sh

# Start cron in background
service cron start

# Start Streamlit in foreground
streamlit run viewer2.py --server.port=8501 --server.address=0.0.0.0
