# CellSense AI - start the dashboard (Windows). Backend should be running on :8000.
Push-Location frontend
if (-not (Test-Path node_modules)) {
    Write-Host "Installing frontend dependencies (first run)..." -ForegroundColor Cyan
    npm install
}
Write-Host "Starting dashboard at http://localhost:5173" -ForegroundColor Green
npm run dev
Pop-Location
