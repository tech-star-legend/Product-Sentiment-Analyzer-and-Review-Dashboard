@echo off
echo ============================================================
echo   SentimentScope - Product Sentiment Analyzer Setup
echo ============================================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

:: Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed. Please install from https://nodejs.org
    pause
    exit /b 1
)

echo [1/4] Setting up Python virtual environment...
cd backend
python -m venv venv
call venv\Scripts\activate

echo [2/4] Installing Python dependencies...
pip install -r requirements.txt

echo [3/4] Downloading TextBlob corpora...
python -m textblob.download_corpora

echo [4/4] Installing frontend dependencies...
cd ..\frontend
npm install

echo.
echo ============================================================
echo   Setup complete!
echo.
echo   NEXT STEPS:
echo   1. Configure your database:
echo      - Copy backend\.env.example to backend\.env
echo      - Set your MONGO_URI in backend\.env
echo      (See DATABASE_SETUP.md for detailed instructions)
echo.
echo   2. Start the app:
echo      run-windows.bat
echo ============================================================
pause
