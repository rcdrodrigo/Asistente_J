# jarvis/main.py
"""JARVIS v2.0 - Versión completa para Windows."""

import asyncio
import sys
import signal
import re
import logging
import time
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List, Union

from jarvis.config import JarvisSettings, get_settings
from jarvis.core.agent import JarvisAgent, JarvisApplication
from jarvis.utils.logger import setup_logging, get_logger
from jarvis.exceptions import JarvisError
from jarvis.tts_agent import TextToSpeechManager
from typing import Optional

logger = get_logger(__name__)

class JarvisConsoleApp(JarvisApplication):
    """Aplicación de consola para JARVIS."""
    
    def __init__(self, speak_responses: bool = False):
        super().__init__()
        self.is_running = False
        self.speak_responses = speak_responses
        self.tts_manager: Optional[TextToSpeechManager] = None
    
    async def initialize(self):
        """Inicializa la aplicación de consola."""
        await super().initialize()
        if self.speak_responses:
            print("🔊 El modo de respuestas habladas está activado.")
            self.tts_manager = TextToSpeechManager(self.settings)
        self._show_welcome_message()

    async def cleanup(self):
        """Limpia los recursos de la aplicación de consola."""
        if self.tts_manager:
            await self.tts_manager.cleanup()
        await super().cleanup()
    
    def _show_welcome_message(self):
        """Muestra el mensaje de bienvenida."""
        print("="*70)
        print("🚀 JARVIS v2.0 - Asistente de consola")
        print("="*70)
        print("💡 **Comandos especiales:**")
        print("  • 'help' - Mostrar ayuda completa")
        print("  • 'stats' - Estadísticas de la sesión")
        print("  • 'status' - Estado del sistema")
        print("  • 'quit' - Salir de JARVIS")
        print("\n💻 **Ejemplos de uso:**")
        print("  • Ejecuta: print('Hola mundo')")
        print("  • Información del sistema")
        print("  • ¿Cómo crear una función en Python?")
        print("="*70 + "\n")
    
    async def start_console_mode(self):
        """Inicia el modo consola interactivo."""
        try:
            self.is_running = True
            
            while self.is_running:
                try:
                    user_input = input("\nTú: ").strip()
                    
                    if not user_input:
                        continue
                    
                    if user_input.lower() in ('exit', 'quit', 'salir'):
                        print("👋 ¡Hasta luego!")
                        self.is_running = False
                        break
                        
                    # Procesar el mensaje y obtener respuesta
                    start_time = time.perf_counter()
                    response = await self.agent.process_message(user_input)
                    end_time = time.perf_counter()
                    duration = end_time - start_time
                    logger.info(f"Console command processing time: {duration:.4f} seconds")

                    print(f"\n🤖 {response}")

                    # Hablar la respuesta si está activado
                    if self.speak_responses and self.tts_manager:
                        await self.tts_manager.speak(response)
                    
                except KeyboardInterrupt:
                    print("\n👋 ¡Hasta luego!")
                    self.is_running = False
                    break
                except Exception as e:
                    logger.error(f"Error en la consola: {e}", exc_info=True)
                    print(f"\n⚠️  Ocurrió un error: {str(e)}")
        
        except Exception as e:
            logger.critical(f"Error crítico en modo consola: {e}", exc_info=True)
            print(f"\n❌ Error crítico: {str(e)}")
        finally:
            await self.cleanup()

def handle_signal(signum, frame):
    """Maneja señales del sistema."""
    print("\n🛑 Señal de interrupción recibida. Cerrando...")
    sys.exit(0)

async def check_lm_studio_connection(base_url: str) -> bool:
    """Verifica la conexión con el servidor de LM Studio."""
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/models") as response:
                if response.status == 200:
                    return True
                return False
    except Exception as e:
        logger.error(f"Error conectando a LM Studio: {e}")
        return False

async def start_voice_mode(settings):
    """Inicia el modo de voz de JARVIS con soporte para LM Studio."""
    try:
        from jarvis.voice_agent import VoiceJarvisAgent
        
        print("🔍 Verificando conexión con LM Studio...")
        if not await check_lm_studio_connection(settings.lm_studio_base_url):
            print("\n❌ No se pudo conectar a LM Studio. Por favor asegúrate de que:")
            print("  1. LM Studio esté en ejecución")
            print(f"  2. El servidor local esté accesible en {settings.lm_studio_base_url}")
            print("  3. Hayas cargado un modelo en LM Studio")
            return False
        
        print("✅ Conexión con LM Studio establecida correctamente")
        print("🔊 Iniciando modo voz...")
        
        voice_agent = VoiceJarvisAgent(settings)
        await voice_agent.initialize()
        
        print("\n🎙️  Modo voz activo. Presiona Ctrl+C para salir.")
        print("Di 'Jarvis' seguido de tu comando...")
        
        # Mantener el programa en ejecución
        while True:
            await asyncio.sleep(1)
            
    except ImportError as e:
        print("❌ No se pudo cargar el módulo de voz. Asegúrate de tener instaladas las dependencias necesarias.")
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error en modo voz: {e}")
        return False

async def _start_simple_voice_mode(settings):
    """Inicia el modo de voz simple basado en consola."""
    try:
        from jarvis.simple_voice import SimpleVoiceAgent
        print("🔊 Iniciando modo voz simple...")
        voice_agent = SimpleVoiceAgent(settings)
        
        print("\n🎙️  Modo voz simple activo. Presiona Ctrl+C para salir.")
        print("Di 'Jarvis' seguido de tu comando...")
        
        await voice_agent.run()
        return True
        
    except Exception as e:
        print(f"❌ Error en modo voz simple: {e}")
        return False

async def main(speak_responses: bool = False):
    """Función principal."""
    try:
        # Configurar manejador de señales
        signal.signal(signal.SIGINT, handle_signal)
        
        # Cargar configuración
        settings = get_settings()
        
        # Forzar la desactivación del modo voz para la consola
        settings.enable_voice = False

        # Configurar logging
        setup_logging(settings)
        
        # Inicializar y ejecutar la aplicación
        app = JarvisConsoleApp(speak_responses=speak_responses)
        app.settings = settings
        await app.initialize()
        await app.start_console_mode()
        
    except Exception as e:
        logger.critical(f"Error fatal: {e}", exc_info=True)
        print(f"\n❌ Error fatal: {str(e)}")
        return 1
    
    return 0

def print_usage():
    """Muestra información de uso."""
    print("\nUso: python -m jarvis [opciones]")
    print("\nOpciones:")
    print("  --voice           Inicia en modo voz")
    print("  --simple-voice    Inicia en modo voz simple (sin STT)")
    print("  --speak-responses Habla las respuestas en modo consola")
    print("  --help            Muestra esta ayuda\n")
    print("Ejemplos:")
    print("  python -m jarvis                       # Inicia modo consola")
    print("  python -m jarvis --speak-responses   # Inicia modo consola con respuestas habladas")
    print("  python -m jarvis --voice               # Inicia modo voz")
    print("  python -m jarvis --simple-voice      # Inicia modo voz simple\n")

async def cli_main():
    """Entry point para CLI."""
    if "--help" in sys.argv or "-h" in sys.argv:
        print_usage()
        return 0

    speak_responses = "--speak-responses" in sys.argv
        
    if "--voice" in sys.argv:
        settings = get_settings()
        return await start_voice_mode(settings)
    elif "--simple-voice" in sys.argv:
        settings = get_settings()
        return await _start_simple_voice_mode(settings)
    else:
        return await main(speak_responses=speak_responses)

if __name__ == "__main__":
    sys.exit(asyncio.run(cli_main()))
