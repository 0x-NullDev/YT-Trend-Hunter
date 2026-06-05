@echo off
title YT Trend Hunter - Installation
echo ============================================
echo    YT Trend Hunter - AI Opportunity Platform
echo ============================================
echo.
echo [1/5] Checking prerequisites...
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)
echo [OK] Python found

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)
echo [OK] Node.js found

where docker >nul 2>nul
if %errorlevel% equ 0 (
    echo [OK] Docker found (optional - for full stack)
) else (
    echo [INFO] Docker not found - will use local setup
)

echo.
echo [2/5] Setting up Python virtual environment...
echo.

if not exist "backend\venv" (
    python -m venv backend\venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)
echo [OK] Virtual environment created

echo.
echo [3/5] Installing Python dependencies...
echo.

call backend\venv\Scripts\activate.bat
pip install -r backend\requirements.txt -q
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo [OK] Python dependencies installed

echo.
echo [4/5] Installing frontend dependencies...
echo.

cd frontend
call npm install --silent 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)
cd ..
echo [OK] Frontend dependencies installed

echo.
echo [5/5] Setup complete!
echo.
echo ============================================
echo    How to Start
echo ============================================
echo.
echo   Option 1: Full Stack (Docker)
echo     docker-compose up -d
echo.
echo   Option 2: Backend only
echo     cd backend
echo     ..\venv\Scripts\activate
echo     uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
echo.
echo   Option 3: Frontend only
echo     cd frontend
echo     npm run dev
echo.
echo   Then open http://localhost:3000 in your browser
echo.
echo ============================================
echo.
echo Make sure to:
echo   1. Copy .env.example to .env
echo   2. Add your YOUTUBE_API_KEY in .env
echo   3. (Optional) Add AI provider keys
echo.
pause
