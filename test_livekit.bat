@echo off
echo Probando integración con LiveKit...
python -m pytest test_livekit_integration.py -v

REM Mostrar mensaje de finalización
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Prueba completada exitosamente!
    echo Para probar el agente de voz con LiveKit, ejecuta:
    echo    python -m jarvis.main voice
) else (
    echo.
    echo ❌ Error en las pruebas. Verifica la configuración de LiveKit.
    echo Asegúrate de que las variables de entorno estén configuradas correctamente.
)

pause
