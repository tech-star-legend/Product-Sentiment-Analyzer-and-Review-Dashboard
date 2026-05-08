@echo off
echo Starting SentimentScope...
echo.

:: Start backend in new window
start "SentimentScope Backend" cmd /k "cd backend && venv\Scripts\activate && python app.py"

:: Wait a moment for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend
start "SentimentScope Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ✓ Backend starting on  http://localhost:5000
echo ✓ Frontend starting on http://localhost:3000
echo.
echo Opening browser...
timeout /t 4 /nobreak >nul
start http://localhost:3000
