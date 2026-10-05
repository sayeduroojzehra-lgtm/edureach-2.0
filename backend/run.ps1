Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       Starting EduReach High-Performance Backend       " -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Python Version: " -NoNewline
python --version
Write-Host ""
Write-Host "Starting FastAPI with Uvicorn on http://127.0.0.1:8000 ..." -ForegroundColor Green
Write-Host "Swagger UI docs: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "System Dashboard: http://127.0.0.1:8000/" -ForegroundColor Green
Write-Host ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
