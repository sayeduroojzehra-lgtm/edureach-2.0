@echo off
echo ========================================================
echo        Starting EduReach High-Performance Backend       
echo ========================================================
echo.
echo Checking Python environment...
python --version
echo.
echo Starting FastAPI with Uvicorn on http://127.0.0.1:8000 ...
echo Swagger UI docs available at: http://127.0.0.1:8000/docs
echo System Dashboard available at: http://127.0.0.1:8000/
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
