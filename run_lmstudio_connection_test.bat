@echo off
echo 🚀 Iniciando prueba de conexión con LM Studio
echo =====================================

echo Verificando dependencias...
pip install aiohttp

if %errorlevel% neq 0 (
    echo ❌ Error al instalar dependencias
    pause
    exit /b 1
)

echo.
echo Ejecutando prueba de conexión...
python test_lm_studio_connection.py

if %errorlevel% neq 0 (
    echo.
    echo ============================================
    echo PRUEBA FALLIDA
    echo ============================================
    echo 1. Asegúrate de que LM Studio esté en ejecución
    echo 2. Verifica que el servidor local esté habilitado
    echo 3. Comprueba que el puerto 1234 esté disponible
    echo 4. Revisa el mensaje de error anterior
    echo ============================================
) else (
    echo.
    echo ============================================
    echo PRUEBA COMPLETADA CON ÉXITO
    echo ============================================
)

pause
