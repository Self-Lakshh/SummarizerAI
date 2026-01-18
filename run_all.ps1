# Launch Backend and Frontend Together
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SummarizerAI - Full Stack Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting both backend and frontend..." -ForegroundColor Green
Write-Host ""
Write-Host "Backend: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Gray
Write-Host ""

# Get the current directory
$rootDir = Get-Location

# Start backend in new terminal
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootDir'; .\run_backend.ps1"

# Wait 3 seconds for backend to start
Write-Host "Waiting for backend to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# Start frontend in new terminal
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootDir'; .\run_frontend.ps1"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Both servers launched!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend: http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "Close the terminal windows to stop the servers" -ForegroundColor Gray
