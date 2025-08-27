"""
Agente de voz para JARVIS con soporte offline.

Este módulo proporciona capacidades de reconocimiento y síntesis de voz
utilizando bibliotecas locales sin dependencias de servicios en la nube.
"""

import asyncio
import json
import os
import logging
import time
import aiohttp
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Callable, Awaitable, Union
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

import pyttsx3
import speech_recognition as sr
from faster_whisper import WhisperModel

from .config import JarvisSettings, get_settings
from .exceptions import (
    VoiceError, 
    SpeechRecognitionError, 
    SpeechSynthesisError,
    handle_error
)

# Configure logger
logger = logging.getLogger(__name__)

# Type aliases
AudioData = bytes
Text = str
VoiceCommandHandler = Callable[[str], Awaitable[Optional[Text]]]

class VoiceState(Enum):
    """Estados del agente de voz."""
    IDLE = auto()
    LISTENING = auto()
    PROCESSING = auto()
    SPEAKING = auto()
    ERROR = auto()

@dataclass
class TTSOptions:
    """Opciones de configuración para la síntesis de voz."""
    rate: int = 175  # Palabras por minuto
    volume: float = 1.0  # 0.0 a 1.0
    voice_id: Optional[str] = None
    save_to_file: bool = False
    output_file: Optional[Path] = None


class PyTTSX3Engine:
    """Motor de síntesis de voz utilizando pyttsx3."""
    
    def __init__(self, settings: Optional[JarvisSettings] = None):
        """Inicializa el motor de síntesis de voz.
        
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
        logger.info("Motor de síntesis de voz inicializado")
    
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
                if hasattr(voice, 'languages') and voice.languages:
                    if lang_code in voice.languages[0].lower():
                        self.engine.setProperty('voice', voice.id)
                        logger.debug(f"Voz configurada: {voice.name} ({voice.id})")
                        return
            
            logger.warning(f"No se encontró una voz para el idioma '{lang_code}'. Usando voz por defecto.")
                
        except Exception as e:
            logger.warning(f"No se pudo configurar la voz: {e}")
    
    @handle_error(default_return=None, raise_custom=SpeechSynthesisError)
    async def synthesize(
        self, 
        text: str, 
        options: Optional[TTSOptions] = None
    ) -> Optional[bytes]:
        """Sintetiza texto a voz de manera asíncrona.
        
        Args:
            text: Texto a sintetizar.
            options: Opciones de síntesis. Si no se proporciona, se usan las predeterminadas.
            
        Returns:
            bytes: Audio generado en formato WAV o None si hay un error.
            
        Raises:
            SpeechSynthesisError: Si hay un error al sintetizar el texto.
        """
        if not text.strip():
            logger.warning("Se intentó sintetizar un texto vacío")
            return None
            
        options = options or self._current_options
        self._current_options = options
        self._stop_requested.clear()
        self._is_speaking.set()
        
        try:
            # Actualizar propiedades del motor
            self.engine.setProperty('rate', options.rate)
            self.engine.setProperty('volume', options.volume)
            
            if options.voice_id:
                self.engine.setProperty('voice', options.voice_id)
            
            # Ejecutar en un hilo separado
            loop = asyncio.get_running_loop()
            
            if options.save_to_file and options.output_file:
                # Guardar a archivo de forma asíncrona
                output_path = Path(options.output_file).with_suffix('.wav')
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                def save_to_file():
                    self.engine.save_to_file(text, str(output_path))
                    self.engine.runAndWait()
                    return output_path
                
                file_path = await loop.run_in_executor(self.executor, save_to_file)
                logger.debug(f"Audio guardado en: {file_path}")
                
                # Leer el archivo generado y devolverlo
                if file_path.exists():
                    with open(file_path, 'rb') as f:
                        return f.read()
                return None
                
            else:
                # Reproducir directamente
                await loop.run_in_executor(
                    self.executor, 
                    self.engine.say,
                    text
                )
                await loop.run_in_executor(
                    self.executor, 
                    self.engine.runAndWait
                )
                return None
                
        except Exception as e:
            logger.error(f"Error al sintetizar voz: {e}", exc_info=True)
            raise SpeechSynthesisError(
                f"Error al sintetizar voz: {str(e)}",
                text=text,
                options=options.__dict__
            )
            
        finally:
            self._is_speaking.clear()
    
    async def stop(self) -> None:
        """Detiene la reproducción de voz actual."""
        self._stop_requested.set()
        # pyttsx3 no tiene un método stop directo, pero podemos intentar interrumpir
        if self._is_speaking.is_set():
            try:
                self.engine.stop()
                # Reiniciar el motor para limpiar el estado
                self.engine = self._init_engine()
            except Exception as e:
                logger.warning(f"Error al detener la reproducción: {e}")
    
    async def cleanup(self) -> None:
        """Libera los recursos del motor de síntesis de voz."""
        try:
            await self.stop()
            self.executor.shutdown(wait=True)
            logger.info("Motor de síntesis de voz liberado")
        except Exception as e:
            logger.error(f"Error al limpiar el motor de síntesis: {e}")
    
    def __del__(self):
        """Asegura la liberación de recursos al destruir la instancia."""
        if hasattr(self, 'executor') and self.executor:
            self.executor.shutdown(wait=False)


class WhisperSTT:
    """Clase para reconocimiento de voz usando Whisper."""
    
    def __init__(self, settings: Optional[JarvisSettings] = None):
        """Inicializa el reconocedor de voz con Whisper.
        
        Args:
            settings: Configuración de JARVIS. Si no se proporciona, se cargará.
        """
        self.settings = settings or get_settings()
        self.model = None
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="STT-Thread")
        self._is_initialized = False
        self._model_lock = asyncio.Lock()
        
    async def initialize(self) -> None:
        """Inicializa el modelo de Whisper de forma asíncrona."""
        if self._is_initialized:
            return
            
        async with self._model_lock:
            if not self._is_initialized:  # Doble verificación para evitar condiciones de carrera
                try:
                    loop = asyncio.get_running_loop()
                    self.model = await loop.run_in_executor(
                        self.executor,
                        lambda: WhisperModel(
                            self.settings.whisper_model,
                            device=self.settings.whisper_device,
                            compute_type="int8"  # Balance entre rendimiento y precisión
                        )
                    )
                    self._is_initialized = True
                    logger.info(f"Modelo Whisper cargado: {self.settings.whisper_model}")
                except Exception as e:
                    logger.error(f"Error al cargar el modelo Whisper: {e}", exc_info=True)
                    raise SpeechRecognitionError(
                        f"No se pudo cargar el modelo de reconocimiento de voz: {e}"
                    )
    
    @handle_error(default_return=None, raise_custom=SpeechRecognitionError)
    async def transcribe(self, audio_data: bytes, language: Optional[str] = None) -> str:
        """Transcribe audio a texto usando Whisper.
        
        Args:
            audio_data: Datos de audio en formato WAV.
            language: Código de idioma (ej: 'es', 'en'). Si es None, se detecta automáticamente.
            
        Returns:
            str: Texto transcrito.
            
        Raises:
            SpeechRecognitionError: Si hay un error en el reconocimiento.
        """
        if not self._is_initialized:
            await self.initialize()
            
        if not audio_data:
            raise ValueError("No se proporcionaron datos de audio")
            
        try:
            # Guardar temporalmente el audio para procesarlo con Whisper
            temp_file = Path("temp_whisper_audio.wav")
            with open(temp_file, "wb") as f:
                f.write(audio_data)
                
            # Transcribir usando Whisper
            loop = asyncio.get_running_loop()
            segments, _ = await loop.run_in_executor(
                self.executor,
                lambda: self.model.transcribe(
                    str(temp_file),
                    language=language or self.settings.voice_language,
                    beam_size=5  # Balance entre velocidad y precisión
                )
            )
            
            # Unir los segmentos de texto
            text = " ".join(segment.text for segment in segments if hasattr(segment, 'text'))
            
            # Limpiar archivo temporal
            temp_file.unlink(missing_ok=True)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error en la transcripción: {e}", exc_info=True)
            raise SpeechRecognitionError(
                f"Error al transcribir audio: {e}",
                audio_length=len(audio_data),
                language=language
            )
    
    async def cleanup(self) -> None:
        """Libera los recursos del reconocedor de voz."""
        try:
            if hasattr(self, 'executor') and self.executor:
                self.executor.shutdown(wait=True)
            logger.info("Recursos del reconocedor de voz liberados")
        except Exception as e:
            logger.error(f"Error al limpiar el reconocedor de voz: {e}")


class VoiceJarvisAgent:
    """Agente JARVIS con capacidades de voz offline."""
    
    def __init__(self, settings: Optional[JarvisSettings] = None):
        """Inicializa el agente de voz con configuración offline.
        
        Args:
            settings: Configuración de JARVIS. Si no se proporciona, se cargará.
        """
        self.settings = settings or get_settings()
        self.state = VoiceState.IDLE
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = PyTTSX3Engine(self.settings)
        self.stt_engine = WhisperSTT(self.settings)
        self._is_listening = False
        self._stop_event = asyncio.Event()
        self._command_handlers: Dict[str, VoiceCommandHandler] = {}
        
        # Configurar reconocedor de voz
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8  # Segundos de silencio para considerar el final de una frase
        self.recognizer.phrase_threshold = 0.3  # Segundos mínimos de audio para considerar como frase
        
        # Registrar manejadores de comandos por defecto
        self._register_default_handlers()
        self.is_listening = False
        self.stop_listening = None
        
        # Inicializar el modelo de Whisper para reconocimiento de voz
        self.whisper_model = WhisperModel(
            self.settings.whisper_model,
            device=self.settings.whisper_device,
            compute_type="int8"  # Mejor compatibilidad con CPU
        )
        
        # Inicializar el motor de texto a voz
        self.tts_engine = PyTTSX3Engine()
        
        # Configurar el reconocedor de voz
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)  # Calibrar con ruido ambiente
        self.settings = settings
        self.llm = None
        self.stt_engine = None
        self.tts_engine = None
        self.voice_commands = self._setup_voice_commands()
        self.active_sessions: Dict[str, 'VoiceSession'] = {}
        
    async def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
        """
        Escucha el micrófono y transcribe el audio a texto usando Whisper.
        
        Args:
            timeout: Tiempo máximo de espera para que comience el habla (segundos)
            phrase_time_limit: Tiempo máximo de grabación (segundos)
            
        Returns:
            str: Texto transcrito o None si no se detectó habla
        """
        if not self.settings.enable_voice:
            logger.warning("El reconocimiento de voz está deshabilitado en la configuración")
            return None
            
        with self.microphone as source:
            logger.info("Escuchando... (di algo)")
            try:
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
                # Guardar audio temporal para depuración
                temp_audio = "temp_audio.wav"
                with open(temp_audio, "wb") as f:
                    f.write(audio.get_wav_data())
                
                # Transcribir con Whisper
                segments, _ = self.whisper_model.transcribe(
                    temp_audio,
                    language=self.settings.voice_language,
                    beam_size=5  # Balance entre velocidad y precisión
                )
                
                # Unir todos los segmentos de texto
                text = " ".join([segment.text for segment in segments])
                
                # Limpiar
                os.remove(temp_audio)
                
                if not text.strip():
                    logger.warning("No se detectó habla")
                    return None
                    
                logger.info(f"Transcripción: {text}")
                return text.strip()
                
            except sr.WaitTimeoutError:
                logger.info("Tiempo de espera agotado")
                return None
            except Exception as e:
                logger.error(f"Error en el reconocimiento de voz: {e}")
                return None
    
    async def speak(self, text: str) -> None:
        """
        Reproduce el texto como voz usando pyttsx3.
        
        Args:
            text: Texto a convertir a voz
        """
        if not self.settings.enable_voice:
            logger.warning("La síntesis de voz está deshabilitada en la configuración")
            return
            
        try:
            await self.tts_engine.synthesize(text)
        except Exception as e:
            logger.error(f"Error al reproducir voz: {e}")
    
    async def start_voice_loop(self) -> None:
        """Inicia el bucle principal de reconocimiento de voz."""
        if not self.settings.enable_voice:
            logger.warning("El modo de voz está deshabilitado en la configuración")
            return
            
        logger.info("Iniciando bucle de voz...")
        self.is_listening = True
        
        try:
            while self.is_listening:
                # Escuchar comando de voz
                command = await self.listen()
                
                if command:
                    # Procesar comando
                    response = await self.process_command(command)
                    
                    # Responder por voz
                    if response:
                        await self.speak(response)
                        
        except KeyboardInterrupt:
            logger.info("Deteniendo el bucle de voz...")
        except Exception as e:
            logger.error(f"Error en el bucle de voz: {e}")
        finally:
            await self.cleanup()
    
    async def process_command(self, command: str) -> Optional[str]:
        """
        Procesa un comando de voz y devuelve una respuesta.
        
        Args:
            command: Comando de voz a procesar
            
        Returns:
            str: Respuesta al comando o None si no hay respuesta
        """
        # Convertir a minúsculas para hacer coincidencias más fáciles
        command = command.lower()
        
        # Comandos básicos
        if any(saludo in command for saludo in ["hola", "buenos días", "buenas tardes"]):
            return f"¡Hola! ¿En qué puedo ayudarte?"
            
        elif any(despedida in command for despedida in ["adiós", "hasta luego", "nos vemos"]):
            self.is_listening = False
            return "Hasta luego. ¡Que tengas un buen día!"
            
        # Aquí puedes agregar más comandos personalizados
        
        return "No entendí ese comando. ¿Podrías repetirlo?"
    
    async def cleanup(self) -> None:
        """Limpia los recursos del agente de voz."""
        if hasattr(self, 'tts_engine') and self.tts_engine:
            await self.tts_engine.cleanup()
        
        if hasattr(self, 'whisper_model'):
            del self.whisper_model
            
        logger.info("Recursos del agente de voz liberados")
    
    def _setup_voice_commands(self) -> Dict[str, callable]:
        """Define los comandos de voz y sus manejadores."""
        return {
            "hola": self._handle_greeting,
            "adiós": self._handle_goodbye,
            "ayuda": self._handle_help,
            "estado": self._handle_status,
        }
    
    async def process_voice_command(self, session_id: str, text: str) -> str:
        """Process a voice command and return a response."""
        text = text.lower().strip()
        
        # Check for exact matches first
        if text in self.voice_commands:
            return await self.voice_commands[text](session_id)
            
        # Check for partial matches
        for cmd, handler in self.voice_commands.items():
            if cmd in text:
                return await handler(session_id)
        
        # No command matched, use LLM for general response
        return await self._handle_general_query(session_id, text)
    
    async def _handle_greeting(self, session_id: str) -> str:
        """Handle greeting command."""
        return "¡Hola! Soy JARVIS, tu asistente de voz. ¿En qué puedo ayudarte hoy?"
    
    async def _handle_goodbye(self, session_id: str) -> str:
        """Handle goodbye command."""
        return "¡Hasta luego! Si necesitas algo más, aquí estaré."
    
    async def _handle_help(self, session_id: str) -> str:
        """Handle help command."""
        commands = ", ".join(self.voice_commands.keys())
        return f"Puedes decirme: {commands}. O simplemente hazme cualquier pregunta."

    async def _handle_general_query(self, session_id: str, query: str) -> str:
        """
        Handle general user queries using LM Studio.
        
        Args:
            session_id: ID of the current voice session
            query: User's query text
            
        Returns:
            str: Response from LM Studio
        """
        if not query or not query.strip():
            return "No he recibido ninguna consulta. ¿Podrías repetir?"
            
        try:
            import aiohttp
            import json
            from urllib.parse import urljoin
            
            # Get LM Studio settings
            base_url = self.settings.lm_studio_base_url
            model = self.settings.lm_studio_model
            temperature = self.settings.lm_studio_temperature
            max_tokens = self.settings.lm_studio_max_tokens
            
            # Prepare the API endpoint
            url = urljoin(base_url, "chat/completions")
            
            # Get conversation history for context
            if session_id in self.active_sessions:
                conversation = self.active_sessions[session_id].get('conversation', [])
            else:
                conversation = []
                
            # Add the new user message
            conversation.append({"role": "user", "content": query})
            
            # Prepare the request payload
            payload = {
                "model": model,
                "messages": conversation,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            # Make the API request
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        assistant_message = result['choices'][0]['message']['content']
                        
                        # Update conversation history
                        if session_id in self.active_sessions:
                            self.active_sessions[session_id]['conversation'] = conversation
                            self.active_sessions[session_id]['conversation'].append(
                                {"role": "assistant", "content": assistant_message}
                            )
                        
                        return assistant_message.strip()
                    else:
                        error_text = await response.text()
                        logger.error(f"Error from LM Studio API: {error_text}")
                        return "Lo siento, he tenido un problema al procesar tu solicitud. Por favor, inténtalo de nuevo más tarde."
                        
        except Exception as e:
            logger.error(f"Error in _handle_general_query: {str(e)}", exc_info=True)
            return f"Lo siento, ha ocurrido un error: {str(e)}"
    
    async def _initialize_stt(self):
        """Initialize the speech-to-text engine (disabled for local mode)."""
        logger.info("STT engine is disabled for local voice mode to save resources.")
        return None
    
    async def _initialize_tts(self):
        """Initialize the text-to-speech engine using pyttsx3."""
        logger.info("Initializing TTS engine...")
        try:
            self.tts_engine = PyTTSX3Engine()
            logger.info("✅ pyttsx3 TTS engine initialized successfully")
            return self.tts_engine
        except Exception as e:
            logger.warning(f"Failed to initialize pyttsx3 TTS: {e}. TTS will be disabled.")
            return None

    async def cleanup(self):
        """Clean up session resources."""
        self.is_active = False
        self.audio_buffer = bytearray()
        logger.info(f"Ended voice session {self.session_id}")
        
        # Clean up STT/TTS resources if needed
        if self.agent.stt_engine and hasattr(self.agent.stt_engine, 'cleanup'):
            await self.agent.stt_engine.cleanup()
            
        if self.agent.tts_engine and hasattr(self.agent.tts_engine, 'cleanup'):
            await self.agent.tts_engine.cleanup()



