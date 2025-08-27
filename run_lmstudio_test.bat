@echo off
echo LM Studio Test Script
echo ====================

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not in your system PATH
    pause
    exit /b 1
)

echo.
echo Installing required packages...
pip install aiohttp

if %errorlevel% neq 0 (
    echo Error: Failed to install required packages
    pause
    exit /b 1
)

echo.
echo Running LM Studio test...
python test_lmstudio_manual.py

if %errorlevel% neq 0 (
    echo.
    echo =============================================
    echo TROUBLESHOOTING
    echo 1. Make sure LM Studio is running
    echo 2. In LM Studio, go to 'Local Server' tab
    echo 3. Toggle 'Server' to ON
    echo 4. Verify URL is set to: http://localhost:1234
    echo 5. Make sure a model is loaded in LM Studio
    echo =============================================
)

pause
