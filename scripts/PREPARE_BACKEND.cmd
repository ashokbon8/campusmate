@echo off
setlocal
cd /d "%~dp0.."
if exist ".venv\Scripts\python.exe" goto ready
py -3.12 --version >nul 2>nul
if not errorlevel 1 (
  py -3.12 -m venv .venv
  goto ready
)
py -3.11 --version >nul 2>nul
if not errorlevel 1 (
  py -3.11 -m venv .venv
  goto ready
)
echo Install Python 3.12 with the Python launcher, then run this file again.
exit /b 1
:ready
if not exist ".venv\Scripts\python.exe" exit /b 1
".venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" scripts\setup_local.py
if errorlevel 1 exit /b 1
exit /b 0
