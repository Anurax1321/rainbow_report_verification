@echo off
echo.
echo ================================================================================
echo  Neonatal Screening Report Analyzer
echo  Vijayrekha Life Sciences
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo [1/3] Checking Python installation... OK
echo.

REM Check if Streamlit is installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [2/3] Streamlit not found. Installing dependencies...
    echo This may take a few minutes on first run...
    echo.
    python -m pip install --upgrade pip --quiet
    python -m pip install -r requirements.txt --quiet
    echo Dependencies installed successfully!
    echo.
) else (
    echo [2/3] Dependencies already installed... OK
    echo.
)

echo [3/3] Starting application...
echo Browser will open automatically in 3 seconds...
echo.
echo Press Ctrl+C to stop the application
echo ================================================================================
echo.

timeout /t 3 /nobreak > nul
start "" http://localhost:8501

python -m streamlit run app.py

REM If the app crashes, pause so user can see the error
if errorlevel 1 (
    echo.
    echo ================================================================================
    echo Application stopped with an error.
    echo ================================================================================
    pause
)
