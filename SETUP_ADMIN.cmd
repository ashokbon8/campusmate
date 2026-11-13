@echo off
setlocal
cd /d "%~dp0"
call scripts\PREPARE_BACKEND.cmd
if errorlevel 1 goto failed
".venv\Scripts\python.exe" scripts\setup_admin.py %*
if errorlevel 1 goto failed
echo Keep your chosen admin email and password private.
echo Start or restart CampusMate, then click Admin Login.
pause
exit /b 0
:failed
echo Admin setup stopped. No account can be used until setup succeeds and the backend restarts.
pause
exit /b 1
