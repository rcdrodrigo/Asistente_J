@echo off
echo Ejecutando prueba de comandos de voz...
python test_voice_simple.py > voice_test_output.txt 2>&1
type voice_test_output.txt
del voice_test_output.txt
pause
