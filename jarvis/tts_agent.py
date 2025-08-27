"""
Agente de texto a voz (TTS) para JARVIS.

Este módulo proporciona capacidades de síntesis de voz
utilizando bibliotecas locales sin dependencias de servicios en la nube.
"""

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor

import pyttsx3

from .config import JarvisSettings, get_settings
from .exceptions import SpeechSynthesisError

# Configurar logger
logger = logging.getLogger(__name__)

@dataclass
class TTSOptions:
    """Opciones de configuración para la síntesis de voz."""
    rate: int = 175  # Palabras por minuto
    volume: float = 1.0  # 0.0 a 1.0
    voice_id: Optional[str] = None
    save_to_file: bool = False
    output_file: Optional[Path] = None

class TextToSpeechAgent:
    """Agente de texto a voz simplificado para JARVIS."""
    
    def __init__(self, settings: Optional[JarvisSettings] = None):
        """Inicializa el agente de texto a voz.
        
        Args:
            settings: Configuración de JARVIS. Si no se proporciona, se cargará.
        """
        self.settings = settings or get_settings()
        self.engine = self._init_engine()
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="TTS-Thread")
        self._is_speaking = asyncio.Event()
        self._stop_requested = asyncio.Event()
        self._current_options = TTSOptions()
        
        # Configuración inicial
        self._configure_voice()
        logger.info("Agente de texto a voz inicializado")
    
    def _init_engine(self):
        """Inicializa el motor de pyttsx3 con configuración básica."""
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', self._current_options.rate)
            engine.setProperty('volume', self._current_options.volume)
            return engine
        except Exception as e:
            logger.error("No se pudo inicializar el motor de síntesis de voz", exc_info=True)
            raise SpeechSynthesisError(
                "Error al inicializar el motor de síntesis de voz",
                original_error=str(e)
            )
    
    def _configure_voice(self) -> None:
        """Configura la voz según el idioma especificado en la configuración."""
        try:
            voices = self.engine.getProperty('voices')
            lang_code = self.settings.voice_language.lower()
            
            # Buscar una voz que coincida con el idioma
            for voice in voices:
                if lang_code in voice.languages[0].lower() if hasattr(voice, 'languages') and voice.languages else False:
                    self.engine.setProperty('voice', voice.id)
                    logger.info(f"Voz configurada: {voice.name} ({voice.id})")
                    return
            
            logger.warning(f"No se encontró una voz para el idioma {lang_code}. Usando voz predeterminada.")
            
        except Exception as e:
            logger.error(f"Error al configurar la voz: {e}")
    
    async def speak(self, text: str, options: Optional[TTSOptions] = None) -> None:
        """Reproduce el texto como voz.
        
        Args:
            text: Texto a convertir a voz
            options: Opciones de configuración para esta reproducción
        """
        if not text.strip():
            logger.warning("Se intentó reproducir un texto vacío")
            return
            
        if options:
            self._apply_tts_options(options)
        
        try:
            # Usar un executor para no bloquear el bucle de eventos
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                self.executor,
                self._speak_sync,
                text
            )
            
        except Exception as e:
            logger.error(f"Error al reproducir voz: {e}")
            raise SpeechSynthesisError(
                f"Error al reproducir voz: {e}",
                original_error=str(e)
            )
    
    def _speak_sync(self, text: str) -> None:
        """Método síncrono para reproducir voz (se ejecuta en un hilo separado)."""
        try:
            self._is_speaking.set()
            self.engine.say(text)
            self.engine.runAndWait()
        finally:
            self._is_speaking.clear()
    
    def _apply_tts_options(self, options: TTSOptions) -> None:
        """Aplica las opciones de configuración al motor TTS."""
        if options.rate is not None:
            self.engine.setProperty('rate', options.rate)
        if options.volume is not None:
            self.engine.setProperty('volume', options.volume)
        if options.voice_id is not None:
            self.engine.setProperty('voice', options.voice_id)
        
        self._current_options = options
    
    async def stop(self) -> None:
        """Detiene la reproducción de voz actual."""
        if self._is_speaking.is_set():
            self.engine.stop()
            self._is_speaking.clear()
    
    async def cleanup(self) -> None:
        """Libera los recursos del agente de voz."""
        try:
            await self.stop()
            if hasattr(self, 'executor') and self.executor:
                self.executor.shutdown(wait=False)
            logger.info("Recursos del agente de voz liberados")
        except Exception as e:
            logger.error(f"Error al limpiar el agente de voz: {e}")
    
    def get_available_voices(self) -> list:
        """Devuelve una lista de voces disponibles."""
        return [{
            'id': voice.id,
            'name': voice.name,
            'languages': voice.languages if hasattr(voice, 'languages') else ['en']
        } for voice in self.engine.getProperty('voices')]
