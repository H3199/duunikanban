#!/bin/bash
set -e

# Run jobs initially
# /app/backend/runner.sh

# Start cron in background
service cron start

uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 --proxy-headers
