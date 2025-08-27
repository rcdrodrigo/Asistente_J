@echo off
echo Setting up Python environment for JARVIS...

:: Check Python version
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    exit /b 1
)

:: Install required packages
echo Installing required Python packages...
pip install aiohttp

:: Run the test script
echo.
echo Running LM Studio connection test...
python simple_lmstudio_test.py

pause
