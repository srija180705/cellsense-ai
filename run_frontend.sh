#!/usr/bin/env bash
# CellSense AI - start the dashboard (macOS / Linux). Backend should run on :8000.
set -e
cd frontend
[ -d node_modules ] || { echo "Installing frontend dependencies..."; npm install; }
echo "Starting dashboard at http://localhost:5173"
npm run dev
