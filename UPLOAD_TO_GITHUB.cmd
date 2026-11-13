@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto venv
py -3 --version >nul 2>nul
if not errorlevel 1 goto py
python --version >nul 2>nul
if not errorlevel 1 goto python
echo Python was not found. Install Python or run RUN_CAMPUSMATE.cmd first.
goto failed
:venv
".venv\Scripts\python.exe" scripts\upload_to_github.py
goto result
:py
py -3 scripts\upload_to_github.py
goto result
:python
python scripts\upload_to_github.py
:result
if errorlevel 1 goto failed
echo Your complete code is now on GitHub.
pause
exit /b 0
:failed
echo The upload did not finish. Read the message above.
pause
exit /b 1
