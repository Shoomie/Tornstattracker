@echo off
title Faction Crime Tracker

REM Clear the screen
cls

echo Installing/Updating required libraries...
pip install -r requirements.txt
echo.

echo Starting Faction Crime Tracker...
echo =====================================
echo.

REM --- Make sure this filename is EXACTLY correct ---
cls
python Tornstattracker.py
REM ---------------------------------------------------

echo.
echo =====================================
echo Tracker script finished or exited. Press any key to close this window.
echo =====================================
pause > nul