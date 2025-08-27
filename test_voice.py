"""Test script for JARVIS voice functionality."""
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from jarvis.simple_voice import SimpleVoiceAgent
from jarvis.voice_agent import VoiceJarvisAgent
from jarvis.config import JarvisSettings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_simple_voice_agent():
    """Test the simple voice agent with console input."""
    print("\n🚀 Probando agente de voz simple...")
    
    try:
        # Initialize settings
        settings = JarvisSettings()
        
        # Create and initialize the voice agent
        agent = SimpleVoiceAgent(settings)
        await agent.initialize()
        
        # Test commands
        test_commands = [
            "hola",
            "¿cómo estás?",
            "ayuda",
            "estado",
            "adiós"
        ]
        
        # Process each test command
        for cmd in test_commands:
            print(f"\nTú: {cmd}")
            response = await agent.process_text_command(cmd)
            print(f"JARVIS: {response}")
            await asyncio.sleep(0.5)  # Small delay between commands
        
        print("\n✅ Prueba del agente simple completada exitosamente!")
        return True
        
    except Exception as e:
        logger.error(f"Error en la prueba del agente simple: {e}", exc_info=True)
        return False

async def test_livekit_voice_agent():
    """Test the LiveKit voice agent."""
    print("\n🚀 Probando agente de voz con LiveKit...")
    
    try:
        # Initialize settings
        settings = JarvisSettings()
        
        # Check if LiveKit is configured
        if not all([settings.livekit_url, settings.livekit_api_key, settings.livekit_api_secret]):
            print("⚠️ LiveKit no está configurado. Omitiendo prueba de LiveKit.")
            print("   Configura las variables de entorno LIVEKIT_URL, LIVEKIT_API_KEY y LIVEKIT_API_SECRET")
            return False
            
        # Create and initialize the LiveKit voice agent
        agent = VoiceJarvisAgent(settings)
        await agent.initialize()
        
        # Create a test session
        session_id = "test_session"
        await agent.start_voice_session(session_id)
        
        # Test commands
        test_commands = [
            "hola",
            "¿qué puedes hacer?",
            "dime la hora",
            "gracias, adiós"
        ]
        
        # Process each test command
        for cmd in test_commands:
            print(f"\nTú: {cmd}")
            response = await agent.process_voice_command(session_id, cmd)
            print(f"JARVIS: {response}")
            await asyncio.sleep(0.5)  # Small delay between commands
        
        # Clean up
        await agent.end_voice_session(session_id)
        
        print("\n✅ Prueba de LiveKit completada exitosamente!")
        return True
        
    except Exception as e:
        logger.error(f"Error en la prueba de LiveKit: {e}", exc_info=True)
        return False

async def main():
    """Run all voice agent tests."""
    print("=" * 50)
    print("🔊 PRUEBAS DE VOZ DE JARVIS")
    print("=" * 50)
    
    # Test simple voice agent
    simple_ok = await test_simple_voice_agent()
    
    # Test LiveKit voice agent
    livekit_ok = await test_livekit_voice_agent()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("-" * 50)
    print(f"✅ Agente de voz simple: {'Éxito' if simple_ok else 'Falló'}")
    print(f"✅ Agente de voz LiveKit: {'Éxito' if livekit_ok else 'Falló o omitido'}")
    print("=" * 50)
    
    # Exit with appropriate status
    if not simple_ok:
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Prueba interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)
        sys.exit(1)
