# JARVIS - Voice Capabilities

This document provides instructions for setting up and using the voice capabilities in JARVIS.

## Prerequisites

1. **LiveKit Account**
   - Sign up at [LiveKit Cloud](https://cloud.livekit.io/)
   - Create a new project and get your API key and secret
   - Note your LiveKit URL (usually in the format `wss://your-instance.livekit.cloud`)

2. **Optional: DeepGram Account (for improved speech-to-text)**
   - Sign up at [DeepGram](https://console.deepgram.com/)
   - Create an API key

3. **Optional: ElevenLabs Account (for improved text-to-speech)**
   - Sign up at [ElevenLabs](https://beta.elevenlabs.io/)
   - Get your API key from the profile section

## Installation

1. Install the required Python packages:
   ```bash
   pip install livekit livekit-agents livekit-agents[openai,deepgram,elevenlabs]
   ```

2. Copy the example environment file and update it with your credentials:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file and fill in your API keys and configuration.

## Configuration

### Required Environment Variables

```env
# LiveKit Configuration
LIVEKIT_URL=wss://your-livekit-instance.livekit.cloud
LIVEKIT_API_KEY=your_api_key_here
LIVEKIT_API_SECRET=your_api_secret_here

# Enable voice mode
ENABLE_VOICE=true
```

### Optional Configuration

```env
# Voice settings
VOICE_PROVIDER=livekit  # livekit, elevenlabs, openai
VOICE_MODEL=nova
VOICE_LANGUAGE=es

# STT (Speech-to-Text)
STT_PROVIDER=deepgram  # deepgram, whisper
DEEPGRAM_API_KEY=your_deepgram_api_key_here

# TTS (Text-to-Speech)
TTS_PROVIDER=elevenlabs  # elevenlabs, cartesia
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
CARTESIA_API_KEY=your_cartesia_api_key_here
```

## Usage

### Starting Voice Mode

To start JARVIS in voice mode, run:

```bash
python -m jarvis.main voice
```

Or in Spanish:

```bash
python -m jarvis.main voz
```

### Voice Commands

JARVIS supports the following voice commands in Spanish:

- **Greeting**: "Hola JARVIS", "Buenos días"
- **Farewell**: "Adiós", "Hasta luego"
- **Help**: "Ayuda", "¿Qué puedes hacer?"
- **Status**: "¿Cómo estás?", "¿Estás funcionando?"

### Customizing Voice Commands

You can customize the voice commands by modifying the `voice_command_patterns` in the `config.py` file.

## Troubleshooting

### Common Issues

1. **No Audio Input/Output**
   - Ensure your microphone and speakers are properly connected
   - Check your system's audio settings
   - Try running the application with administrator privileges

2. **Connection Issues**
   - Verify your LiveKit URL, API key, and secret are correct
   - Check your internet connection
   - Ensure any required ports are open in your firewall

3. **Speech Recognition Issues**
   - Speak clearly and at a moderate pace
   - Reduce background noise
   - Try using DeepGram for improved recognition (requires API key)

## Development

### Adding New Voice Commands

1. Edit the `voice_tools.py` file
2. Add a new method to handle the command
3. Add the command pattern to the `VoiceCommandRecognizer` class
4. Update the help text to include the new command

### Testing

To test the voice agent without LiveKit:

```python
from jarvis.voice_agent import VoiceJarvisAgent
from jarvis.config import JarvisSettings

settings = JarvisSettings()
agent = VoiceJarvisAgent(settings)

# Test voice command processing
response = asyncio.run(agent.process_voice_command("test_session", "Hola JARVIS"))
print(response)
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
