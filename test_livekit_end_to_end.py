"""End-to-end test for LiveKit voice integration."""
import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LiveKitTestRunner:
    """Runner for end-to-end LiveKit tests."""
    
    def __init__(self):
        self.settings = None
        self.voice_agent = None
        self.room = None
        self.connected = False
    
    async def initialize(self):
        """Initialize the test runner."""
        from jarvis.config import JarvisSettings
        from jarvis.voice_agent import VoiceJarvisAgent
        
        logger.info("Initializing test runner...")
        
        # Load settings
        self.settings = JarvisSettings()
        
        # Verify LiveKit configuration
        if not all([
            self.settings.livekit_url,
            self.settings.livekit_api_key,
            self.settings.livekit_api_secret
        ]):
            raise ValueError("LiveKit configuration is incomplete. Please check your .env file.")
        
        # Initialize voice agent
        self.voice_agent = VoiceJarvisAgent(self.settings)
        await self.voice_agent.initialize()
        
        logger.info("Test runner initialized successfully.")
    
    async def connect_to_room(self, room_name: str = "test-room"):
        """Connect to a LiveKit room."""
        try:
            from livekit import rtc, api
            
            logger.info(f"Connecting to room: {room_name}")
            
            # Create a LiveKit client
            livekit = api.LiveKitAPI(
                url=self.settings.livekit_url,
                api_key=self.settings.livekit_api_key,
                api_secret=self.settings.livekit_api_secret,
            )
            
            # Create a room
            self.room = rtc.Room()
            
            # Set up event handlers
            @self.room.on("connected")
            def on_connected():
                logger.info("Connected to room")
                self.connected = True
            
            @self.room.on("disconnected")
            def on_disconnected():
                logger.info("Disconnected from room")
                self.connected = False
            
            # Connect to the room
            token = livekit.create_token(
                identity="test-runner",
                room_name=room_name,
                can_publish=True,
                can_subscribe=True,
            )
            
            await self.room.connect(
                self.settings.livekit_url,
                token,
                auto_subscribe=True,
            )
            
            logger.info("Successfully connected to the room")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to room: {e}", exc_info=True)
            return False
    
    async def test_voice_session(self):
        """Test a voice session with the LiveKit agent."""
        if not self.connected or not self.room:
            logger.error("Not connected to a room")
            return False
        
        try:
            logger.info("Starting voice session test...")
            
            # Create a test session
            session_id = f"test-session-{os.getpid()}"
            session = await self.voice_agent.start_voice_session(session_id)
            
            # Test commands
            test_commands = [
                "hola",
                "¿qué puedes hacer?",
                "dime la hora",
                "gracias, adiós"
            ]
            
            # Process each test command
            for cmd in test_commands:
                logger.info(f"Sending command: {cmd}")
                response = await self.voice_agent.process_voice_command(session_id, cmd)
                logger.info(f"Response: {response}")
                await asyncio.sleep(1)  # Small delay between commands
            
            # Clean up
            await self.voice_agent.end_voice_session(session_id)
            
            logger.info("Voice session test completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error in voice session test: {e}", exc_info=True)
            return False
    
    async def cleanup(self):
        """Clean up resources."""
        try:
            if self.room and self.connected:
                await self.room.disconnect()
                self.connected = False
                
            if self.voice_agent:
                # Clean up any remaining sessions
                for session_id in list(self.voice_agent.active_sessions.keys()):
                    await self.voice_agent.end_voice_session(session_id)
                
                # Clean up the agent
                if hasattr(self.voice_agent, 'cleanup'):
                    await self.voice_agent.cleanup()
                    
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)


async def main():
    """Run the end-to-end test."""
    print("=" * 50)
    print("🔊 PRUEBA DE INTEGRACIÓN DE LIVEKIT")
    print("=" * 50)
    
    runner = LiveKitTestRunner()
    
    try:
        # Initialize the test runner
        await runner.initialize()
        
        # Connect to a test room
        if not await runner.connect_to_room("jarvis-test"):
            print("\n❌ No se pudo conectar a la sala de LiveKit")
            print("   Verifica que el servidor esté en ejecución y las credenciales sean correctas.")
            return 1
        
        # Run the voice session test
        if await runner.test_voice_session():
            print("\n✅ ¡Prueba de integración completada con éxito!")
            return 0
        else:
            print("\n❌ La prueba de integración falló. Revisa los logs para más detalles.")
            return 1
            
    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)
        print(f"\n❌ Error inesperado: {e}")
        return 1
        
    finally:
        # Clean up resources
        await runner.cleanup()
        print("\n✨ Prueba finalizada")


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\n❌ Prueba interrumpida por el usuario")
        sys.exit(1)
