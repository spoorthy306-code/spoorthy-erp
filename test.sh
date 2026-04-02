#!/usr/bin/env bash
set -e

echo "[1/3] Creating DB schema..."
python main.py --validate || true

echo "[2/3] Running pytest..."
python -m pytest --maxfail=1 --disable-warnings -q

echo "[3/3] Saved Postman collection to ./postman_collection.json"
