@echo off
echo Testing Python environment...
python --version
if %errorlevel% neq 0 (
    echo Python is not in the system PATH
    exit /b 1
)

echo.
echo Testing LM Studio connection...
python -c "import aiohttp, asyncio; asyncio.run((lambda: __import__('aiohttp').ClientSession().get('http://localhost:1234/v1/models'))())"
