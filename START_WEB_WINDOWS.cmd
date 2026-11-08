@echo off
setlocal
cd /d "%~dp0"
echo Spiritual Vibez - start the web app and backend
echo.
set "SV_PYTHON="
py -3.11 --version >nul 2>&1
if not errorlevel 1 set "SV_PYTHON=py -3.11"
if not defined SV_PYTHON (
  python --version >nul 2>&1
  if not errorlevel 1 set "SV_PYTHON=python"
)
if not defined SV_PYTHON (
  py -3 --version >nul 2>&1
  if not errorlevel 1 set "SV_PYTHON=py -3"
)
if not defined SV_PYTHON (
  echo Install Python 3.11 or newer from https://www.python.org/downloads/windows/
  if not defined CI pause
  exit /b 1
)
%SV_PYTHON% "%~dp0run_web.py" %*
if errorlevel 1 (
  echo.
  echo Extract the complete project ZIP and use Python 3.11 or newer.
  echo Read the error above, then start this file again.
  if not defined CI pause
  exit /b 1
)
