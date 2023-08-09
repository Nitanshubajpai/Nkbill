@echo off

REM Navigate to your Django project directory
cd /d C:\DEll\nkbill\nkbill

REM Activate the virtual environment (if you're using one)
REM Replace "venv" with the name of your virtual environment folder
REM If you're not using a virtual environment, you can skip this step
call C:\DEll\nkbill\env\Scripts\activate

REM Set any required environment variables (if needed)
REM For example, if you have a SECRET_KEY environment variable:
REM set SECRET_KEY=your_secret_key_value

REM Run the Django development server
start cmd /k python manage.py runserver

REM Open the URL in the default web browser after a short delay (adjust as needed)
ping 127.0.0.1 -n 2 > nul
start "" http://127.0.0.1:8000
