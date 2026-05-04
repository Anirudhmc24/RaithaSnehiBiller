@echo off
title SLV Traders - Shop Manager
color 0A

echo.
echo  ==========================================
echo   Sri Lakshmi Venkateshwara Traders
echo   Shop Management + GST Registers
echo  ==========================================
echo.

cd /d "%~dp0"

:: ── Check Python ───────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found!
    echo.
    echo  Please download Python from https://python.org
    echo  During install, TICK the box "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo  Python found:
python --version

:: ── Install / verify ALL required packages ─────────────────────────────────
echo.
echo  Checking and installing packages (may take 1-2 min first time)...
pip install streamlit reportlab xlsxwriter openpyxl requests pandas -q --no-warn-script-location

if errorlevel 1 (
    echo.
    echo  WARNING: Some packages may not have installed correctly.
    echo  Trying to continue anyway...
)
echo  Packages ready.

:: ── Quick import check — shows actual error if something is wrong ───────────
echo.
echo  Running startup check...
python -c "import streamlit, reportlab, xlsxwriter, openpyxl, requests, pandas; print('  All OK')"
if errorlevel 1 (
    echo.
    echo  ==========================================
    echo   STARTUP ERROR — see message above
    echo   Screenshot this window and share it.
    echo  ==========================================
    echo.
    pause
    exit /b 1
)

:: ── Launch ─────────────────────────────────────────────────────────────────
echo.
echo  ==========================================
echo   Opening SLV Traders...
echo   Browser opens at http://localhost:8501
echo   DO NOT close this window while using.
echo  ==========================================
echo.

powershell -Command "Start-Sleep -Seconds 3; Start-Process 'http://localhost:8501'"
python -m streamlit run "%~dp0app.py" --server.port 8501 --server.headless false --browser.gatherUsageStats false

:: ── If we get here, streamlit stopped ──────────────────────────────────────
echo.
echo  App stopped.
echo  If it crashed, scroll up to read the error message.
echo.
pause
