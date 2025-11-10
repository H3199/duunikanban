#!/usr/bin/env bash
set -euo pipefail

DATE=$(date -I)

OUTDIR="jaysons"
mkdir -p "$OUTDIR"

FI_FILE="${OUTDIR}/fi_${DATE}.json"
EMEA_FILE="${OUTDIR}/emea_${DATE}.json"

echo "Running daily job fetch for ${DATE}"

if [ "$MOCK" = "1" ]; then
    echo "Running in MOCK mode: copying example JSONs instead of querying API..."
    cp /app/jaysons/mock_data/fi_sample.json /app/jaysons/fi_latest.json
    cp /app/jaysons/mock_data/emea_sample.json /app/jaysons/emea_latest.json
else
    echo "Fetching Finnish jobs..."
    ./fi_jobs.py > "$FI_FILE"
    echo "Saved: $FI_FILE"

    echo "Fetching EMEA jobs..."
    ./emea_jobs.py > "$EMEA_FILE"
    echo "Saved: $EMEA_FILE"
fi

cp "$FI_FILE" "${OUTDIR}/fi_latest.json"
cp "$EMEA_FILE" "${OUTDIR}/emea_latest.json"
