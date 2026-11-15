@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher not found. Install Python 3.11 or 3.12 from python.org first.
  pause
  exit /b 1
)
if not exist .venv\Scripts\python.exe (
  py -3.11 -m venv .venv
  if errorlevel 1 py -3.12 -m venv .venv
)
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto :error
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :error
.venv\Scripts\python.exe -m pytest -q
if errorlevel 1 goto :error
echo.
echo Starting CyberShield AI dashboard...
.venv\Scripts\python.exe -m streamlit run app.py
exit /b 0
:error
echo Setup or tests failed. Read the error above.
pause
exit /b 1
