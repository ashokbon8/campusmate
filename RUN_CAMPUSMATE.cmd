@echo off
setlocal
cd /d "%~dp0"
set CAMPUSMATE_DATASET=jscoe
set CAMPUSMATE_SEED=1
echo CampusMate Final - preparing your website
call scripts\PREPARE_BACKEND.cmd
if errorlevel 1 goto failed
".venv\Scripts\python.exe" scripts\first_run.py %*
if errorlevel 1 goto failed
".venv\Scripts\python.exe" scripts\run_local.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo CampusMate stopped. Read the message above for the next step.
pause
exit /b 1
