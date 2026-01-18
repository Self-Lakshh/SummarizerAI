# Run Backend Locally - Windows
# Make sure you have activated your virtual environment first

Write-Host "Starting SummarizerAI Backend..." -ForegroundColor Green
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Warning: Virtual environment not detected!" -ForegroundColor Yellow
    Write-Host "Activate it with: venv\Scripts\activate" -ForegroundColor Yellow
    Write-Host ""
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found!" -ForegroundColor Yellow
    Write-Host "Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "Please edit .env with your configuration" -ForegroundColor Yellow
    Write-Host ""
}

# Create necessary directories
Write-Host "Creating directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "uploads", "faiss_indices", "logs" | Out-Null

# Run the server
Write-Host "Starting FastAPI server..." -ForegroundColor Cyan
Write-Host ""
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Health Check: http://localhost:8000/health" -ForegroundColor Green
Write-Host ""

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
