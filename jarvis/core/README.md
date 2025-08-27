# JARVIS Core Modules

This directory contains the core components of the JARVIS Voice Agent, designed for professional, enterprise-grade voice interactions.

## Core Components

### 1. Voice Agent (`voice_agent.py`)
The main voice agent implementation with support for:
- Speech-to-text (STT) using Whisper
- Text-to-speech (TTS) using pyttsx3
- Wake word detection
- Audio processing and enhancement
- Session management

### 2. Enterprise Features (`enterprise.py`)
Professional features including:
- User authentication and authorization
- Session management
- Role-based access control
- Audit logging
- Rate limiting

### 3. Error Handling (`error_handling.py`)
Robust error management with:
- Custom exception hierarchy
- Automatic retries with backoff
- Error recovery strategies
- Error monitoring and reporting

### 4. Metrics (`metrics.py`)
Performance monitoring:
- System metrics (CPU, memory, etc.)
- Custom application metrics
- Performance statistics
- Resource usage tracking

## Getting Started

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Basic Usage**:
   ```python
   from jarvis.core.voice_agent import VoiceAgent
   from jarvis.core.enterprise import SessionManager
   from jarvis.core.metrics import metrics
   import asyncio
   
   async def main():
       # Initialize components
       agent = VoiceAgent()
       session_manager = SessionManager()
       
       # Start metrics collection
       await metrics.start_system_metrics()
       
       # Start a session
       session = await agent.start_session()
       
       # Process voice input
       response = await agent.process_voice(audio_data)
       print(f"Assistant: {response}")
   
   if __name__ == "__main__":
       asyncio.run(main())
   ```

## Configuration

Configuration is handled through environment variables or a `.env` file:

```env
# Voice settings
VOICE_LANGUAGE=es
SAMPLE_RATE=16000

# Security
MAX_SESSIONS=100
SESSION_TIMEOUT=1800

# Performance
MAX_WORKERS=4
AUDIO_BUFFER_SIZE=4096
```

## Error Handling

The agent includes comprehensive error handling:

```python
from jarvis.core.error_handling import with_error_handling

@with_error_handling(component="voice_agent", max_retries=3)
async def process_audio(audio_data):
    # Processing logic here
    pass
```

## Monitoring

Monitor performance using the metrics system:

```python
# Record custom metric
await metrics.record("audio_processing_time", processing_time_ms)

# Get statistics
stats = metrics.get_stats("audio_processing_time")
print(f"Average processing time: {stats['avg']:.2f}ms")
```

## Security

- All passwords are hashed using PBKDF2-HMAC-SHA256
- Session tokens are cryptographically secure
- Rate limiting prevents abuse
- Audit logging for all sensitive operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
