@echo off
echo ========================================================
echo        Running EduReach Backend Automated Tests         
echo ========================================================
echo.
python -m pytest tests/ -v
echo.
pause
