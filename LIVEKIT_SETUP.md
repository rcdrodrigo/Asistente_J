# LiveKit Voice Integration for JARVIS

This guide explains how to set up and use the LiveKit voice integration with JARVIS.

## Prerequisites

1. Python 3.8 or higher
2. LiveKit server (self-hosted or cloud)
3. API keys for STT/TTS services (Deepgram, ElevenLabs, etc.)

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install livekit-server-sdk livekit-agents livekit-plugins[openai,deepgram,elevenlabs] python-dotenv
   ```

2. **Configure environment variables**:
   Copy `.env.example` to `.env` and update the following variables:
   ```
   # LiveKit Configuration
   LIVEKIT_URL=wss://your-livekit-instance.livekit.cloud
   LIVEKIT_API_KEY=your_api_key_here
   LIVEKIT_API_SECRET=your_api_secret_here
   
   # Voice Configuration
   ENABLE_VOICE=true
   VOICE_PROVIDER=livekit
   
   # STT Configuration (Deepgram recommended)
   STT_PROVIDER=deepgram
   DEEPGRAM_API_KEY=your_deepgram_api_key
   
   # TTS Configuration (ElevenLabs recommended)
   TTS_PROVIDER=elevenlabs
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   ```

## Running the Voice Agent

1. **Start the LiveKit worker**:
   ```bash
   python test_livekit.py
   ```

2. **Connect to the LiveKit room**:
   - Use the LiveKit CLI, web client, or mobile app to connect to your LiveKit server
   - Join the room specified in the `.env` file (default: `jarvis`)
   - The worker will automatically process audio from participants

## Testing

1. **Basic voice commands**:
   - "Hola JARVIS" - Greet the assistant
   - "¿Qué puedes hacer?" - Get help
   - "¿Cómo estás?" - Check status
   - "Adiós" - End the session

2. **Custom commands**:
   Add custom commands by extending the `_setup_voice_commands` method in `voice_agent.py`

## Troubleshooting

1. **No audio detected**:
   - Check your microphone permissions
   - Verify the STT service is properly configured
   - Check LiveKit server logs for connection issues

2. **No response from JARVIS**:
   - Verify the worker is running and connected to LiveKit
   - Check the logs for any errors
   - Ensure your API keys are valid

3. **Poor speech recognition**:
   - Try speaking more clearly
   - Adjust the silence threshold in `VoiceSession` class if needed
   - Consider using a different STT provider

## Development

- The main voice agent logic is in `jarvis/voice_agent.py`
- Voice commands are defined in the `_setup_voice_commands` method
- Audio processing happens in the `VoiceSession` class

## License

This project is licensed under the MIT License - see the LICENSE file for details.
