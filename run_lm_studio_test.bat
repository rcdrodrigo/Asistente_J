@echo off
setlocal

:: Set Python path (update this to your Python executable path if needed)
set PYTHON=python

:: Add current directory to Python path
set PYTHONPATH=%~dp0

:: Install required packages
%PYTHON% -m pip install -r requirements.txt

:: Run the test
%PYTHON% test_lm_studio_direct.py

pause
