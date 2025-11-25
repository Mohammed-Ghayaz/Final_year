@echo off
REM DR PDF to Excel Converter - Launcher
REM This script starts the web application automatically

title Delivery Request PDF to Excel Converter
color 0A

echo.
echo ========================================
echo Delivery Request PDF to Excel Converter
echo ========================================
echo.
echo Starting the application...
echo.

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org
    pause
    exit /b 1
)

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    python -m pip install flask pandas openpyxl pdfplumber pillow opencv-python pytesseract -q
)

REM Start the Flask app
echo.
echo ✓ Starting server...
echo.
echo Open your browser and go to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
