@echo off
echo JARVIS Diagnostic Tool
echo =====================

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your system PATH
    pause
    exit /b 1
)

echo.
echo Running diagnostic script...
python simple_diagnostic.py

if %errorlevel% neq 0 (
    echo.
    echo ============================================
    echo DIAGNOSTIC FAILED
    echo ============================================
    echo 1. Make sure Python is installed correctly
    echo 2. Check if the script exists: simple_diagnostic.py
    echo 3. Try running: python --version
    echo 4. Check Python is in your system PATH
    echo ============================================
) else (
    echo.
    echo ============================================
    echo DIAGNOSTIC COMPLETED
    echo Check the results above for any issues
    echo ============================================
)

pause
