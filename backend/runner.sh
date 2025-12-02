#!/usr/bin/env bash
set -euo pipefail

DATE=$(date -I)

# TODO recreate mock mode, this is a remnant from json-file era.
# MOCK=${MOCK:-0}

echo "Running daily job fetch for ${DATE}"

#if [ "$MOCK" = "1" ]; then
#    echo "Running in MOCK mode: test data instead of querying API..."
#else
#    echo "Running in live mode: querying API..."
#fi

echo "Fetching Finnish jobs..."
python3 ./fi_jobs.py

echo "Fetching EMEA jobs..."
python3 ./emea_jobs.py
