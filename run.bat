@echo off
setlocal EnableDelayedExpansion

REM ============================================================
REM  Nkbill - Start Server
REM  Double-click or run from any location — no hardcoded paths.
REM ============================================================

REM Change to the folder this script lives in
cd /d "%~dp0"

REM --- Check setup has been run ---
if not exist "env\Scripts\activate.bat" (
    echo.
    echo  ERROR: Virtual environment not found.
    echo  Please run setup.bat first.
    echo.
    pause
    exit /b 1
)

if not exist "db.sqlite3" (
    echo.
    echo  WARNING: Database not found.
    echo  Please run setup.bat first to create the database.
    echo.
    pause
    exit /b 1
)

REM --- Activate environment ---
call env\Scripts\activate.bat

REM --- Start the server in a new window ---
echo.
echo  Starting Nkbill server...
echo  The app will open in your browser automatically.
echo.
start "Nkbill Server" cmd /k "cd /d "%~dp0" && call env\Scripts\activate.bat && python manage.py runserver"

REM --- Wait briefly for the server to start then open browser ---
ping 127.0.0.1 -n 3 >nul
start "" http://127.0.0.1:8000
