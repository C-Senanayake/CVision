@echo off
echo Cleaning up old connections...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul

timeout /t 2 /nobreak >nul

echo Starting FastAPI server...
uvicorn main:app --reload --host 127.0.0.1 --port 8000 --timeout-keep-alive 5