@echo off
setlocal EnableDelayedExpansion

REM ============================================================
REM  Nkbill - First-time Setup Script
REM  Run this once before using the app for the first time.
REM ============================================================

REM Change to the folder this script lives in (no hardcoded paths)
cd /d "%~dp0"

echo.
echo  =============================================
echo   Billing Setup
echo  =============================================
echo.

REM --- Step 1: Check Python is available ---
echo [1/4] Checking for Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Python was not found on this system.
    echo  Please install Python 3.9+ from https://www.python.org/downloads/
    echo  Make sure to tick "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo  Found: %PYVER%

REM --- Step 2: Create virtual environment ---
echo.
echo [2/4] Creating virtual environment in .\env ...
if exist "env\Scripts\activate.bat" (
    echo  Virtual environment already exists. Skipping creation.
) else (
    python -m venv env
    if %errorlevel% neq 0 (
        echo  ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo  Virtual environment created.
)

REM --- Step 3: Install requirements ---
echo.
echo [3/4] Installing requirements from requirements.txt ...
call env\Scripts\activate.bat
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo  ERROR: pip install failed. Check requirements.txt and your internet connection.
    pause
    exit /b 1
)
echo  Requirements installed.

REM --- Step 4: Run database migrations ---
echo.
echo [4/4] Running database migrations ...
python manage.py migrate
if %errorlevel% neq 0 (
    echo  ERROR: Migration failed.
    pause
    exit /b 1
)

REM --- Done ---
echo.
echo  =============================================
echo   Setup complete!
echo.
echo   Run  run.bat  to start the server.
echo  =============================================
echo.
pause
