# JARVIS - Asistente Personal

Un asistente de voz personal con capacidades de procesamiento de lenguaje natural local, optimizado para funcionar con LM Studio.

## Características Principales

- 🎙️ **Voz en Tiem Real** con procesamiento local
- 🧠 **Procesamiento de Lenguaje Natural** local con LM Studio
- 🔒 **Privacidad Total** - Todo el procesamiento se realiza localmente
- 🚀 **Rápido y Eficiente** - Optimizado para hardware personal
- 🎙️ **Control por Voz** - Interacción natural y fluida
- 🛠️ **Personalizable** - Adaptado a tus necesidades específicas

## Requisitos

- Python 3.9 o superior
- [LM Studio](https://lmstudio.ai/) ejecutándose con el servidor de API habilitado
- Micrófono (para entrada de voz)
- Altavoces (para salida de voz)
- Conexión a Internet (solo para la instalación inicial)

## Configuración de LM Studio

Para usar JARVIS con LM Studio, sigue estos pasos:

1. Descarga e instala [LM Studio](https://lmstudio.ai/) en tu computadora
2. Inicia LM Studio y selecciona un modelo de lenguaje compatible
3. Habilita el servidor de API local:
   - Ve a la pestaña "Local Server" en la interfaz de LM Studio
   - Asegúrate de que el servidor esté configurado para escuchar en `0.0.0.0:1234`
   - Haz clic en "Start Server"
4. Verifica que el servidor esté funcionando abriendo `http://localhost:1234/v1/models` en tu navegador

## Configuración de JARVIS

JARVIS está configurado por defecto para conectarse a LM Studio en `http://localhost:1234/v1`. Si necesitas cambiar esta configuración, edita el archivo `.env` o modifica la configuración directamente en `jarvis/config.py`.

## Instalación Rápida

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/jarvis.git
   cd jarvis
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuración**
   ```bash
   cp .env.example .env
   ```
   Edita el archivo `.env` con tus preferencias personales.

## Uso Básico

### Configuración del Proveedor LM Studio

Puedes configurar el proveedor LM Studio de dos maneras:

1. **Usando la configuración por defecto**:
   ```python
   from jarvis.providers.factory import LLMProviderFactory
   
   async def main():
       # Crea un proveedor con la configuración por defecto
       provider = await LLMProviderFactory.create("lm_studio")
   ```

2. **Personalizando la configuración**:
   ```python
   from jarvis.providers.lm_studio import LMStudioConfig, LMStudioProvider
   
   config = LMStudioConfig(
       base_url="http://localhost:1234/v1",
       model="tu-modelo-local",
       temperature=0.7,
       max_tokens=2000,
       top_p=0.9,
       timeout=300
   )
   
   provider = LMStudioProvider(config)
   ```

### Uso con el Agente Principal

```python
from jarvis import JARVIS

async def main():
    # Inicializa JARVIS con el proveedor LM Studio
    jarvis = JARVIS(llm_provider="lm_studio")
    
    # Realiza una consulta
    response = await jarvis.ask("Hola, ¿cómo estás?")
    print(f"JARVIS: {response}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Pruebas de Integración

Para verificar que la integración con LM Studio está funcionando correctamente, ejecuta:

```bash
python test_lm_studio_direct.py
```

## Solución de Problemas

### El servidor de LM Studio no responde
- Asegúrate de que LM Studio esté en ejecución con el servidor de API habilitado
- Verifica que el puerto 1234 no esté siendo usado por otra aplicación
- Comprueba que la URL base en la configuración de JARVIS coincida con la de LM Studio

### Error de conexión
- Verifica que tu firewall no esté bloqueando las conexiones locales
- Asegúrate de que LM Studio esté configurado para aceptar conexiones desde otras redes si estás usando una IP distinta a localhost

### Rendimiento lento
- Prueba con un modelo más pequeño si tu hardware es limitado
- Ajusta los parámetros de generación (temperature, max_tokens) para mejorar el rendimiento

## Agente de Texto a Voz (TTS)

El agente de texto a voz permite convertir texto en voz hablada de forma local, sin necesidad de servicios en la nube.

#### Ejemplo Rápido

```python
import asyncio
from jarvis import TextToSpeechAgent

async def main():
    tts = TextToSpeechAgent()
    await tts.speak("¡Hola! Soy JARVIS, tu asistente de voz.")
    await tts.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

#### Opciones de Configuración

Puedes personalizar la voz, velocidad y volumen:

```python
from jarvis import TextToSpeechAgent, TTSOptions

async def speak_with_options():
    tts = TextToSpeechAgent()
    options = TTSOptions(
        rate=150,      # Palabras por minuto (70-200)
        volume=0.8,    # Volumen (0.0 a 1.0)
    )
    await tts.speak("Texto con opciones personalizadas", options=options)
    await tts.cleanup()
```

#### Ejecutar Ejemplo

El repositorio incluye un ejemplo completo en `examples/tts_example.py`:

```bash
python examples/tts_example.py
```

### Iniciar JARVIS con Interfaz de Voz Completa
```bash
python -m jarvis.main voice
```

### Comandos de Voz Principales
- "Hola JARVIS" - Activar el asistente
- "Abre [aplicación]" - Abrir aplicaciones
- "Busca en internet [término]" - Realizar búsquedas
- "Escribe un correo sobre [tema]" - Redactar correos
- "Configura un recordatorio para [hora] [tarea]" - Establecer recordatorios

### Personalización
Puedes personalizar los comandos editando el archivo `config/commands.json`

## Configuración de LM Studio

1. Descarga e instala [LM Studio](https://lmstudio.ai/)
2. Descarga el modelo de lenguaje que prefieras
3. En LM Studio, inicia el servidor local (puerto 1234)
4. Asegúrate de que la URL en `.env` apunte a `http://localhost:1234/v1`

## Documentación

- [Configuración de Voz con LiveKit](LIVEKIT_VOICE_SETUP.md) - Guía detallada para la integración de voz
- [Estructura del Proyecto](docs/STRUCTURE.md) - Organización del código
- [Desarrollo de Módulos](docs/DEVELOPMENT.md) - Cómo extender JARVIS

## Dependencias Principales

- **LiveKit**: Comunicación de voz en tiempo real
- **Deepgram/Whisper**: Reconocimiento de voz (STT)
- **ElevenLabs/Cartesia**: Síntesis de voz (TTS)
- **Ollama/OpenAI**: Modelos de lenguaje

## Requisitos del Sistema

- Python 3.8+
- Servidor LiveKit (local o en la nube)
- Conexión a Internet para servicios en la nube
- 4GB RAM mínimo (8GB recomendado)

## Contribuir

1. Haz un fork del repositorio
2. Crea una rama para tu característica (`git checkout -b feature/awesome-feature`)
3. Haz commit de tus cambios (`git commit -am 'Add awesome feature'`)
4. Haz push a la rama (`git push origin feature/awesome-feature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.
```

### Ollama
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama server
ollama serve &

# Download deepseek-coder model
ollama pull deepseek-coder:6.7b
```

## Project Structure

- `jarvis/` - Main package
  - `core/` - Core functionality
  - `providers/` - Service providers
  - `tools/` - Utility tools
  - `security/` - Security-related code
  - `monitoring/` - Monitoring and logging
  - `utils/` - Helper utilities
- `tests/` - Test suites
  - `unit/` - Unit tests
  - `integration/` - Integration tests
  - `e2e/` - End-to-end tests
- `docs/` - Documentation
- `logs/` - Log files
- `config/` - Configuration files
- `sandbox/` - Testing and experimentation
- `scripts/` - Utility scripts
