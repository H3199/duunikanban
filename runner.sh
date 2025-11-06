#!/usr/bin/env bash
set -euo pipefail

DATE=$(date -I)

OUTDIR="jaysons"
mkdir -p "$OUTDIR"

FI_FILE="${OUTDIR}/fi_${DATE}.json"
EMEA_FILE="${OUTDIR}/emea_${DATE}.json"

echo "Running daily job fetch for ${DATE}"

echo "Fetching Finnish jobs..."
./fi_jobs.py > "$FI_FILE"
echo "Saved: $FI_FILE"

echo "Fetching EMEA jobs..."
./emea_jobs.py > "$EMEA_FILE"
echo "Saved: $EMEA_FILE"

cp "$FI_FILE" "${OUTDIR}/fi_latest.json"
cp "$EMEA_FILE" "${OUTDIR}/emea_latest.json"
