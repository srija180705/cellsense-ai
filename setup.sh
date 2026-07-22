#!/usr/bin/env bash
# CellSense AI - one-time local setup (macOS / Linux)
set -e
echo "Creating virtual environment (.venv)..."
python3 -m venv .venv
echo "Installing dependencies..."
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
echo ""
echo "Setup complete. Download the NASA dataset (see README), then run: ./run_backend.sh"
