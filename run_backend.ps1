# CellSense AI - build data/models if needed, then start the API (Windows)
$py = ".\.venv\Scripts\python.exe"

if (-not (Test-Path "models\artifacts\metrics.json")) {
    Write-Host "Training SoH/RUL models (first run)..." -ForegroundColor Cyan
    & $py models\training\build_dataset.py
    & $py models\training\train.py
}
if (-not (Test-Path "datasets\processed\fleet_features.csv")) {
    Write-Host "Building fleet table..." -ForegroundColor Cyan
    & $py models\training\build_fleet.py
}

Write-Host "Starting API at http://localhost:8000  (docs at /docs)" -ForegroundColor Green
& $py -m uvicorn backend.main:app --reload --port 8000
