@echo off
REM Speech Emotion Recognition System - Windows Setup Script
REM This script sets up the entire project for Windows 10/11

echo.
echo ========================================
echo Speech Emotion Recognition System Setup
echo ========================================
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.13.12 from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [OK] Python is installed

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Node.js is not installed
    echo Please install Node.js from https://nodejs.org/
    echo You can continue with backend only, or install Node.js and run this script again
)

REM Create virtual environment
echo.
echo Creating Python virtual environment...
cd backend
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip, continuing anyway...
)

REM Install Python dependencies
echo.
echo Installing Python dependencies...
echo This may take a few minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies
    echo Check your internet connection and try again
    pause
    exit /b 1
)

echo [OK] Python dependencies installed

REM Install frontend dependencies (if Node.js is available)
node --version >nul 2>&1
if not errorlevel 1 (
    echo.
    echo Installing Node.js dependencies for frontend...
    cd ../frontend
    call npm install
    if errorlevel 1 (
        echo [WARNING] Failed to install frontend dependencies
    ) else (
        echo [OK] Frontend dependencies installed
    )
    cd ../backend
)

REM Create necessary directories
echo.
echo Creating necessary directories...
if not exist "uploads" mkdir uploads
if not exist "models" mkdir models
if not exist "logs" mkdir logs
echo [OK] Directories created

REM Create .env file
echo.
echo Creating .env configuration file...
(
    echo FLASK_ENV=development
    echo FLASK_DEBUG=True
    echo MODEL_PATH=models/best_emotion_model.h5
    echo UPLOAD_FOLDER=uploads
    echo MAX_CONTENT_LENGTH=52428800
    echo CORS_ORIGINS=http://localhost:3000,http://localhost:5000
) > .env
echo [OK] .env file created

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the application:
echo.
echo 1. Open a terminal and navigate to this directory
echo 2. Activate virtual environment:
echo    backend\venv\Scripts\activate
echo.
echo 3. Start the Flask backend:
echo    python app.py
echo    (Server will run at http://localhost:5000)
echo.
echo 4. Open another terminal in the frontend folder and run:
echo    npm start
echo    (Frontend will open at http://localhost:3000)
echo.
echo For more information, see README.md
echo.
pause
