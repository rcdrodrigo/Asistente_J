"""Integration test for LiveKit voice functionality."""
import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_livekit_connection():
    """Test LiveKit connection and basic functionality."""
    from livekit import rtc
    from livekit.agents import (
        JobContext,
        JobRequest,
        WorkerOptions,
        cli,
    )
    
    # Load environment variables
    load_dotenv()
    
    # Get LiveKit configuration
    livekit_url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    
    if not all([livekit_url, api_key, api_secret]):
        logger.error("LiveKit configuration is missing. Please check your .env file.")
        return False
    
    logger.info("Testing LiveKit connection...")
    
    try:
        # Test basic LiveKit API connection
        from livekit import api
        livekit = api.LiveKitAPI(
            url=livekit_url,
            api_key=api_key,
            api_secret=api_secret,
        )
        
        # List rooms as a test
        rooms = await livekit.room.list_rooms()
        logger.info(f"Connected to LiveKit. Found {len(rooms)} rooms.")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to connect to LiveKit: {e}")
        return False

async def test_voice_agent():
    """Test the voice agent with LiveKit."""
    from jarvis.voice_agent import VoiceJarvisAgent
    from jarvis.config import JarvisSettings
    
    # Load environment variables
    load_dotenv()
    
    # Initialize settings
    settings = JarvisSettings()
    
    # Check if LiveKit is configured
    if not all([settings.livekit_url, settings.livekit_api_key, settings.livekit_api_secret]):
        logger.error("LiveKit configuration is missing. Please check your .env file.")
        return False
    
    logger.info("Testing VoiceJarvisAgent with LiveKit...")
    
    try:
        # Initialize the agent
        agent = VoiceJarvisAgent(settings)
        await agent.initialize()
        
        # Test voice command processing
        test_commands = [
            "hola",
            "¿qué puedes hacer?",
            "¿cómo estás?",
            "adiós"
        ]
        
        session_id = "test_session"
        
        for cmd in test_commands:
            logger.info(f"Testing command: {cmd}")
            response = await agent.process_voice_command(session_id, cmd)
            logger.info(f"Response: {response}")
        
        # Clean up
        await agent.end_voice_session(session_id)
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing voice agent: {e}", exc_info=True)
        return False

async def main():
    """Run all tests."""
    logger.info("=== Starting LiveKit Integration Tests ===")
    
    # Test 1: LiveKit Connection
    logger.info("\n--- Testing LiveKit Connection ---")
    connection_ok = await test_livekit_connection()
    
    if not connection_ok:
        logger.error("LiveKit connection test failed. Please check your configuration.")
        return
    
    # Test 2: Voice Agent
    logger.info("\n--- Testing Voice Agent ---")
    agent_ok = await test_voice_agent()
    
    if agent_ok:
        logger.info("\n✅ All tests passed!")
    else:
        logger.error("\n❌ Some tests failed. Please check the logs for details.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nTest stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
