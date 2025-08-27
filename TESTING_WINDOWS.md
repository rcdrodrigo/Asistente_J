# Pruebas en Windows

Este documento explica cómo probar JARVIS en un entorno Windows.

## Requisitos previos

1. Python 3.8 o superior instalado
2. Ollama instalado y en ejecución
3. Modelo `deepseek-coder:6.7b` descargado en Ollama

## Configuración inicial

1. **Clonar el repositorio** (si aún no lo has hecho):
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd Asistente_J
   ```

2. **Crear y activar un entorno virtual** (recomendado):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install aiohttp pydantic psutil
   ```

4. **Iniciar Ollama** (en una terminal aparte):
   ```bash
   ollama serve
   ```

## Ejecutar pruebas

Para ejecutar las pruebas de JARVIS en Windows:

```bash
python test_jarvis.py
```

Este script realizará las siguientes comprobaciones:
1. Verificará que Ollama esté en ejecución
2. Probará la conexión con el modelo `deepseek-coder:6.7b`
3. Enviará un prompt de prueba y mostrará la respuesta

## Solución de problemas

### Ollama no responde
- Asegúrate de que Ollama esté en ejecución: `ollama serve`
- Verifica que puedas acceder a la API: `curl http://localhost:11434/api/version`

### Error de conexión
- Verifica que no haya firewalls bloqueando el puerto 11434
- Asegúrate de que el modelo esté descargado: `ollama pull deepseek-coder:6.7b`

### Problemas de rendimiento
- Si las respuestas son lentas, intenta reducir el tamaño del contexto o el número de tokens máximos
- En equipos con poca RAM, considera usar un modelo más pequeño

## Configuración avanzada

Puedes modificar el archivo `.env` para ajustar la configuración:

```ini
# Configuración de Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-coder:6.7b

# Configuración de rendimiento
MAX_TOKENS=2000
TEMPERATURE=0.7
```

## Soporte

Si encuentras algún problema, por favor:
1. Revisa los logs en `logs/jarvis.log`
2. Verifica que todos los requisitos estén instalados
3. Abre un issue en el repositorio con los detalles del error
