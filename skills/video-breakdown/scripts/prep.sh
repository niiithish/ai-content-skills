#!/usr/bin/env bash
# Kept for old notes that call prep.sh: runs the local analyzer.
exec python3 "$(cd "$(dirname "$0")" && pwd)/breakdown.py" analyze "$@"
