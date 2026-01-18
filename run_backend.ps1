# Backend Startup Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting SummarizerAI Backend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to backend folder
Set-Location backend

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "⚠️  Virtual environment not found!" -ForegroundColor Yellow
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "✓ Activating virtual environment..." -ForegroundColor Green
.\venv\Scripts\Activate.ps1

# Check if dependencies are installed
Write-Host "✓ Checking dependencies..." -ForegroundColor Green
$packagesInstalled = pip list 2>$null | Select-String "fastapi"
if (-not $packagesInstalled) {
    Write-Host "⚠️  Dependencies not installed!" -ForegroundColor Yellow
    Write-Host "Installing requirements..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found!" -ForegroundColor Yellow
    Write-Host "Please create .env file from .env.example and add your OPENAI_API_KEY" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Backend Starting on http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start the backend
uvicorn app.main:app --reload
