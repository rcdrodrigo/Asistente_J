@echo off
echo Ejecutando prueba de integración de LiveKit...
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python no está instalado o no está en el PATH.
    echo Por favor, instala Python 3.8 o superior y asegúrate de que esté en el PATH.
    pause
    exit /b 1
)

REM Verificar dependencias
echo Verificando dependencias...
python -m pip install -q -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error al instalar las dependencias.
    pause
    exit /b 1
)

REM Verificar configuración
echo.
echo Verificando configuración de LiveKit...
python check_env.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ La configuración de LiveKit no es correcta.
    echo Por favor, verifica el archivo .env y asegúrate de que todas las variables
    echo de entorno necesarias estén configuradas correctamente.
    pause
    exit /b 1
)

REM Ejecutar la prueba de integración
echo.
echo Iniciando prueba de integración de LiveKit...
python test_livekit_end_to_end.py

REM Mostrar mensaje de finalización
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ ¡Prueba completada exitosamente!
    echo Ahora puedes ejecutar JARVIS en modo voz con el comando:
    echo    python -m jarvis.main voice
) else (
    echo.
    echo ❌ La prueba de integración falló.
    echo Por favor, revisa los mensajes de error anteriores para más detalles.
)

pause
