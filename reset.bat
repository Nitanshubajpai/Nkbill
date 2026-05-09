@echo off
setlocal EnableDelayedExpansion

REM ============================================================
REM  Nkbill - Reset / Fresh Start
REM  Choose between a soft reset (bills only) or full wipe.
REM ============================================================

cd /d "%~dp0"

echo.
echo  =============================================
echo   Billing Reset Tool
echo  =============================================
echo.
echo  Choose an option:
echo.
echo   [1] Soft Reset  - Delete all bills only
echo                     (Company Profile settings are kept)
echo.
echo   [2] Full Reset  - Wipe everything, fresh install
echo                     (All bills AND company profile deleted)
echo.
echo   [3] Cancel
echo.
set /p CHOICE= Enter 1, 2 or 3 and press Enter:

if "%CHOICE%"=="3" goto :cancel
if "%CHOICE%"=="1" goto :soft_reset
if "%CHOICE%"=="2" goto :full_reset

echo  Invalid choice. Exiting.
pause
exit /b 1


REM ============================================================
:soft_reset
REM ============================================================
echo.
echo  WARNING: This will permanently delete ALL bills and items.
echo  Your Company Profile settings will be preserved.
echo.
set /p CONFIRM= Type YES to confirm:

if /i not "%CONFIRM%"=="YES" goto :cancel

REM Activate env
if not exist "env\Scripts\activate.bat" (
    echo  ERROR: Virtual environment not found. Run setup.bat first.
    pause
    exit /b 1
)
call env\Scripts\activate.bat

REM Back up database before wiping
echo.
echo  Backing up database to db.sqlite3.backup ...
if exist "db.sqlite3" copy "db.sqlite3" "db.sqlite3.backup" >nul
echo  Backup saved.

REM Use Django shell to delete only bills and items
echo  Deleting all bills and items...
python manage.py shell -c "from billmanage.models import bill, item; item.objects.all().delete(); bill.objects.all().delete(); print('Done. Bills deleted:', bill.objects.count())"

echo.
echo  =============================================
echo   Soft reset complete.
echo   All bills deleted. Company Profile kept.
echo   Backup saved to db.sqlite3.backup
echo  =============================================
echo.
pause
exit /b 0


REM ============================================================
:full_reset
REM ============================================================
echo.
echo  WARNING: This will PERMANENTLY DELETE all data including
echo  bills, items, and your Company Profile settings.
echo  The database will be fully recreated from scratch.
echo.
set /p CONFIRM1= Type RESET to confirm full wipe:

if /i not "%CONFIRM1%"=="RESET" goto :cancel

REM Activate env
if not exist "env\Scripts\activate.bat" (
    echo  ERROR: Virtual environment not found. Run setup.bat first.
    pause
    exit /b 1
)
call env\Scripts\activate.bat

REM Back up the old database first
echo.
echo  Backing up current database to db.sqlite3.backup ...
if exist "db.sqlite3" copy "db.sqlite3" "db.sqlite3.backup" >nul
echo  Backup saved.

REM Delete media logos (optional — ask user)
echo.
set /p DELMEDIA= Delete uploaded logos too? (Y/N):
if /i "%DELMEDIA%"=="Y" (
    if exist "media\logos" (
        rmdir /s /q "media\logos"
        echo  Logos folder deleted.
    )
)

REM Delete the database
echo  Deleting database...
if exist "db.sqlite3" del "db.sqlite3"

REM Re-run migrations on fresh database
echo  Creating fresh database...
python manage.py migrate

echo.
echo  =============================================
echo   Full reset complete. Fresh database created.
echo   Backup saved to db.sqlite3.backup
echo   Run run.bat to start the server.
echo  =============================================
echo.
pause
exit /b 0


REM ============================================================
:cancel
REM ============================================================
echo.
echo  Reset cancelled. Nothing was changed.
echo.
pause
exit /b 0
