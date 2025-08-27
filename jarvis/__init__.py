"""
JARVIS - Tu asistente personal de voz

Este paquete proporciona la funcionalidad central para el asistente de voz JARVIS,
incluyendo capacidades de texto a voz y procesamiento de comandos de voz.
"""

from .tts_agent import TextToSpeechAgent, TTSOptions

__version__ = "0.1.0"
__all__ = ['TextToSpeechAgent', 'TTSOptions']