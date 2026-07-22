# CellSense AI - one-time local setup (Windows PowerShell)
# Creates a virtual environment and installs all dependencies.

Write-Host "Creating virtual environment (.venv)..." -ForegroundColor Cyan
python -m venv .venv

Write-Host "Upgrading pip..." -ForegroundColor Cyan
.\.venv\Scripts\python.exe -m pip install --upgrade pip

Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Cyan
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host ""
Write-Host "Setup complete." -ForegroundColor Green
Write-Host "Next: download the NASA dataset (see README) into datasets/NASA_Battery/mat/," -ForegroundColor Yellow
Write-Host "then run:  .\run_backend.ps1" -ForegroundColor Yellow
