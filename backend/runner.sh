#!/usr/bin/env bash
set -euo pipefail

DATE=$(date -I)
OUTDIR="jaysons"
mkdir -p "$OUTDIR"

# Default MOCK to 0 if not set
MOCK=${MOCK:-0}

# Filenames for this run
FI_FILE="${OUTDIR}/fi_${DATE}.json"
EMEA_FILE="${OUTDIR}/emea_${DATE}.json"

echo "Running daily job fetch for ${DATE}"

if [ "$MOCK" = "1" ]; then
    echo "Running in MOCK mode: copying example JSONs instead of querying API..."
    cp /app/jaysons/mock_data/fi_sample.json "${OUTDIR}/fi_latest.json"
    cp /app/jaysons/mock_data/emea_sample.json "${OUTDIR}/emea_latest.json"

    # Also create dated copies
    cp /app/jaysons/mock_data/fi_sample.json "$FI_FILE"
    cp /app/jaysons/mock_data/emea_sample.json "$EMEA_FILE"

else
    echo "Fetching Finnish jobs..."
    python3 ./fi_jobs.py > "$FI_FILE"
    echo "Saved: $FI_FILE"

    echo "Fetching EMEA jobs..."
    python3 ./emea_jobs.py > "$EMEA_FILE"
    echo "Saved: $EMEA_FILE"

    # Copy to latest
    cp "$FI_FILE" "${OUTDIR}/fi_latest.json"
    cp "$EMEA_FILE" "${OUTDIR}/emea_latest.json"
fi
