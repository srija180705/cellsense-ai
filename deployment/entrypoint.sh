#!/usr/bin/env bash
# Build models + fleet table on first run (needs the NASA .mat data mounted),
# then start the API. Idempotent: skips build steps if outputs already exist.
set -e

if [ ! -f models/artifacts/metrics.json ]; then
  echo "[entrypoint] Training SoH/RUL models..."
  python models/training/build_dataset.py
  python models/training/train.py
fi

if [ ! -f datasets/processed/fleet_features.csv ]; then
  echo "[entrypoint] Building fleet table..."
  python models/training/build_fleet.py
fi

echo "[entrypoint] Starting API on 0.0.0.0:8000"
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
