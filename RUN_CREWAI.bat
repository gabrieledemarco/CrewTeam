@echo off
REM Windows Batch Script to Run CrewAI Multi-Agent System
REM Double-click this file to launch the CrewAI application

setlocal enabledelayedexpansion

REM Get the directory where this script is located
cd /d "%~dp0"

echo.
echo 🚀 CrewAI Multi-Agent Development System Launcher
echo.
echo 📂 Working Directory: %cd%
echo 🐍 Initializing Python environment...
echo.

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo Please ensure you ran: py -3.12 -m venv venv
    pause
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

REM Verify crewai is installed
echo ✓ Verifying CrewAI installation...
py -c "import crewai; print('  ✅ CrewAI module found')" >nul 2>&1
if errorlevel 1 (
    echo ❌ CrewAI not found. Installing dependencies...
    py -m pip install -q crewai crewai-tools langchain langchain-openai litellm python-dotenv requests PyYAML
)

REM Run the main application
echo.
echo ✓ Launching CrewAI application...
echo.
py src/coding_crew/main.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo ❌ Application exited with error code %errorlevel%
    pause
)

echo.
echo 👋 CrewAI session ended.
pause
