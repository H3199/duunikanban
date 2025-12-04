#!/bin/bash
#PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

set -e

# Run jobs initially
# /app/backend/runner.sh
# Start cron in background
# /usr/sbin/cron

uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
