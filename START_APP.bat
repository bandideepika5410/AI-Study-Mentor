@echo off
title StudyMentor - Local Server
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 server.py
) else (
  python server.py
)
if errorlevel 1 (
  echo.
  echo Could not start Python. Install Python 3 and select "Add Python to PATH".
  pause
)
