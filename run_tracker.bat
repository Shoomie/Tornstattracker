@echo off
title Faction Crime Tracker Launcher

echo Checking for Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ==================================================================
    echo ERROR: Python does not seem to be installed or added to your PATH.
    echo Please install Python 3 from https://www.python.org/downloads/
    echo IMPORTANT: During installation, make sure to check the box that says
    echo            "Add Python to PATH" or "Add python.exe to PATH".
    echo ==================================================================
    pause
    exit /b 1
)

echo Python found.

echo Checking for pip (Python package installer)...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ==================================================================
    echo ERROR: pip (Python's package installer) was not found.
    echo This might mean your Python installation is incomplete or corrupted.
    echo Try reinstalling Python, ensuring "pip" is included and PATH is set.
    echo ==================================================================
    pause
    exit /b 1
)

echo pip found.

echo Installing/Updating required libraries (requests)...
pip install -r requirements.txt --upgrade --user
if errorlevel 1 (
    echo ==================================================================
    echo ERROR: Failed to install required Python libraries.
    echo This could be due to network issues or permissions problems.
    echo Check your internet connection and try running this again.
    echo If it persists, you may need administrator rights (right-click
    echo 'run_tracker.bat' and select 'Run as administrator'), but try
    echo without admin first.
    echo ==================================================================
    pause
    exit /b 1
)

echo Libraries are up to date.
echo.
echo =====================================
echo Starting Faction Crime Tracker...
echo =====================================
echo.

REM Ensure the python script name below matches your actual script file name!
python faction_crime_tracker.py

echo.
echo =====================================
echo Tracker script finished or exited.
echo =====================================
pause