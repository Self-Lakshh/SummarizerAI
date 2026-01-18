# Frontend Startup Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting SummarizerAI Frontend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to frontend folder
Set-Location frontend

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "⚠️  node_modules not found!" -ForegroundColor Yellow
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install --legacy-peer-deps
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Frontend Starting on http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Make sure backend is running on port 8000" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start the frontend
npm run dev
