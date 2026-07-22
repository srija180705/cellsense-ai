#!/usr/bin/env bash
# CellSense AI - build data/models if needed, then start the API (macOS / Linux)
set -e
PY=./.venv/bin/python

if [ ! -f models/artifacts/metrics.json ]; then
  echo "Training SoH/RUL models (first run)..."
  $PY models/training/build_dataset.py
  $PY models/training/train.py
fi
if [ ! -f datasets/processed/fleet_features.csv ]; then
  echo "Building fleet table..."
  $PY models/training/build_fleet.py
fi

echo "Starting API at http://localhost:8000 (docs at /docs)"
$PY -m uvicorn backend.main:app --reload --port 8000
