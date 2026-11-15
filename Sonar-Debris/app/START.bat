
@echo off
title SONAR DEBRIS

echo ======================================
echo          SONAR DEBRIS
echo       Starting Application
echo ======================================

cd /d "%~dp0"

where python >nul 2>nul

if errorlevel 1 (
    echo Python is not installed.
    echo Please install Python 3.11 or later.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Installing required packages...
".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo Starting SONAR DEBRIS...
".venv\Scripts\python.exe" -m streamlit run app/main.py

pause
