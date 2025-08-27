# Configuración de Voz con LiveKit

Esta guía explica cómo configurar y utilizar la integración de voz en tiempo real de JARVIS con LiveKit.

## Requisitos Previos

- Python 3.8 o superior
- Un servidor LiveKit (auto-alojado o en la nube)
- Claves API para los servicios de STT/TTS (Deepgram, ElevenLabs, etc.)

## Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/jarvis.git
   cd jarvis
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   pip install livekit-server-sdk livekit-agents livekit-plugins[openai,deepgram,elevenlabs]
   ```

3. **Configurar variables de entorno**
   Copiar el archivo `.env.example` a `.env` y actualizar con tus credenciales:
   ```
   # LiveKit
   LIVEKIT_URL=wss://tu-servidor.livekit.cloud
   LIVEKIT_API_KEY=tu_api_key
   LIVEKIT_API_SECRET=tu_api_secret
   
   # Voz
   ENABLE_VOICE=true
   VOICE_PROVIDER=livekit
   
   # STT (Reconocimiento de voz)
   STT_PROVIDER=deepgram
   DEEPGRAM_API_KEY=tu_api_key_deepgram
   
   # TTS (Síntesis de voz)
   TTS_PROVIDER=elevenlabs
   ELEVENLABS_API_KEY=tu_api_key_elevenlabs
   ```

## Uso

### Iniciar JARVIS en modo voz

```bash
python -m jarvis.main voice
```

### Probar la integración con LiveKit

1. **Verificar configuración**
   ```bash
   python check_env.py
   ```

2. **Ejecutar pruebas de integración**
   ```bash
   run_livekit_test.bat  # En Windows
   # o
   python test_livekit_end_to_end.py
   ```

## Configuración Avanzada

### Comandos de Voz Personalizados

Puedes agregar comandos personalizados editando el método `_setup_voice_commands` en `jarvis/voice_agent.py`:

```python
def _setup_voice_commands(self):
    commands = {
        # Comandos existentes...
        
        # Agregar nuevo comando
        r'apaga el sistema': self._handle_shutdown,
    }
    return commands

async def _handle_shutdown(self, session_id: str):
    """Maneja el comando para apagar el sistema."""
    return "Apagando el sistema. ¡Hasta luego!"
```

### Configuración de Calidad de Audio

Puedes ajustar la calidad del audio modificando estos parámetros en la clase `VoiceSession`:

```python
def __init__(self, session_id: str, agent: 'VoiceJarvisAgent'):
    # ...
    self.sample_rate = 16000  # Frecuencia de muestreo (Hz)
    self.channels = 1         # Canales de audio (1 = mono, 2 = estéreo)
    self.sample_width = 2     # Ancho de muestra en bytes (2 = 16-bit)
    self.silence_threshold = 0.01  # Umbral de silencio para detección de voz
    self.min_audio_length = 0.5    # Duración mínima de audio para procesar (segundos)
    self.max_silence = 1.5         # Tiempo máximo de silencio permitido (segundos)
```

## Solución de Problemas

### No se detecta audio
- Verifica que el micrófono esté conectado y tenga permisos
- Comprueba que el nivel de entrada de audio sea adecuado
- Ajusta el `silence_threshold` si es necesario

### El agente no responde
- Verifica que el servidor LiveKit esté en ejecución
- Comprueba los logs en busca de errores
- Asegúrate de que las claves API sean válidas

### Calidad de reconocimiento de voz pobre
- Intenta hablar más claro y cerca del micrófono
- Ajusta la configuración de ruido ambiente
- Considera usar un proveedor STT diferente

## Recursos Adicionales

- [Documentación de LiveKit](https://docs.livekit.io/)
- [Guía de Deepgram para STT](https://developers.deepgram.com/)
- [Documentación de ElevenLabs](https://docs.elevenlabs.io/)

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.
