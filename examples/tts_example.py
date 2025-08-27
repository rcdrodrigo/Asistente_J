"""
Ejemplo de uso del agente de texto a voz (TTS) de JARVIS.

Este script muestra cómo usar la clase TextToSpeechManager para convertir texto a voz
y reproducirlo a través de los altavoces del sistema.
"""

import asyncio
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Función principal que muestra el uso básico de TextToSpeechManager."""
    from jarvis import TextToSpeechManager, TTSOptions
    
    # Crear una instancia del agente TTS
    print("Inicializando agente de texto a voz...")
    tts = TextToSpeechManager()
    
    try:
        # Reproducir un mensaje simple
        print("\n--- Reproduciendo mensaje simple ---")
        await tts.speak("¡Hola! Soy JARVIS, tu asistente de voz.")
        
        # Configurar opciones personalizadas
        options = TTSOptions(
            rate=150,      # Velocidad de habla más lenta
            volume=0.8,    # Volumen al 80%
        )
        
        # Reproducir con opciones personalizadas
        print("\n--- Reproduciendo con opciones personalizadas ---")
        await tts.speak("Puedo ajustar mi velocidad y volumen.", options=options)
        
        # Listar voces disponibles
        print("\n--- Voces disponibles ---")
        voices = tts.get_available_voices()
        for i, voice in enumerate(voices, 1):
            print(f"{i}. {voice['name']} (ID: {voice['id']})")
        
        # Reproducir un mensaje más largo
        print("\n--- Reproduciendo mensaje largo ---")
        await tts.speak("""
            Este es un mensaje más largo que demuestra cómo el agente puede manejar 
            texto extenso. La voz debería sonar natural y fluida, incluso con 
            párrafos completos de texto.
        """)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Limpiar recursos
        print("\nLimpiando recursos...")
        await tts.cleanup()
        print("¡Listo!")

if __name__ == "__main__":
    asyncio.run(main())
