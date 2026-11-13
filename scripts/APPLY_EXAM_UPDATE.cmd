@echo off
setlocal
echo Close the old CampusMate backend and frontend windows before continuing.
pause
py -3.12 --version >nul 2>nul
if not errorlevel 1 (
  py -3.12 "%~dp0apply_exam_update.py"
  goto done
)
py -3.11 --version >nul 2>nul
if not errorlevel 1 (
  py -3.11 "%~dp0apply_exam_update.py"
  goto done
)
python "%~dp0apply_exam_update.py"
:done
pause
