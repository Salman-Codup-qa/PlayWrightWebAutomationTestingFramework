@echo off
setlocal

REM -----------------------------------------------------------
REM --- 1. Create the Virtual Environment ---------------------
REM -----------------------------------------------------------
echo.
echo =========================================================
echo == 1. Creating Python Virtual Environment (venv) ========
echo =========================================================
REM The '|| goto :error' ensures the script stops if venv creation fails
python -m venv venv || goto :error

REM -----------------------------------------------------------
REM --- 2. Activate the Venv and Run Commands -----------------
REM -----------------------------------------------------------
echo.
echo =========================================================
echo == 2. Activating venv and Installing Dependencies ========
echo =========================================================

REM The 'call' command is used to execute another batch file (like activate.bat)
REM and return control to the current script.
call venv\Scripts\activate.bat

REM Check if activation was successful before proceeding
if not defined VIRTUAL_ENV (
    echo.
    echo [ERROR] Failed to activate virtual environment.
    goto :error
)

REM --- Install Python Packages ---
echo.
echo Installing Python requirements from requirements.txt...
python -m pip install -r requirements.txt || goto :error

REM --- Install Playwright Browsers ---
echo.
echo Installing Playwright browsers (chromium, firefox, webkit)...
python -m playwright install || goto :error

REM -----------------------------------------------------------
REM --- 3. Complete and Exit ----------------------------------
REM -----------------------------------------------------------
echo.
echo =========================================================
echo == Project Setup Complete! ==============================
echo =========================================================
echo.
echo You are now inside the virtual environment.
echo To run your tests, type: python -m pytest
echo.

:end
pause
exit /b 0

:error
echo.
echo =========================================================
echo == SETUP FAILED! Check the error messages above. =======
echo =========================================================
pause
exit /b 1