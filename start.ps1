#!/usr/bin/env powershell
# DR PDF to Excel Converter - PowerShell Launcher

Write-Host "========================================"
Write-Host "Delivery Request PDF to Excel Converter"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set location to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check if Python is installed
try {
    python --version | Out-Null
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org"
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Flask is installed
$flaskCheck = python -c "import flask" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    python -m pip install flask pandas openpyxl pdfplumber pillow opencv-python pytesseract -q
}

Write-Host ""
Write-Host "✓ Starting server..." -ForegroundColor Green
Write-Host ""
Write-Host "Open your browser and go to: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server"
Write-Host ""

# Start Flask app
python app.py
