"""Test script for LiveKit integration with JARVIS."""
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

async def test_voice_agent():
    """Test the voice agent with LiveKit."""
    from jarvis.voice_agent import VoiceJarvisAgent, start_worker
    from jarvis.config import JarvisSettings
    
    # Load environment variables
    load_dotenv()
    
    # Initialize settings
    settings = JarvisSettings()
    
    # Check if LiveKit is configured
    if not all([settings.livekit_url, settings.livekit_api_key, settings.livekit_api_secret]):
        logger.error("LiveKit configuration is missing. Please check your .env file.")
        return
    
    logger.info("Starting LiveKit worker...")
    
    try:
        # Start the worker in a separate task
        worker_task = asyncio.create_task(start_worker())
        
        logger.info("Worker started. Press Ctrl+C to stop.")
        logger.info(f"Connect to LiveKit room at: {settings.livekit_url}")
        logger.info(f"Worker ID: jarvis_worker")
        
        # Keep the script running
        await asyncio.Event().wait()
        
    except asyncio.CancelledError:
        logger.info("Shutting down worker...")
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass
        logger.info("Worker stopped.")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        if 'worker_task' in locals():
            worker_task.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(test_voice_agent())
    except KeyboardInterrupt:
        logger.info("Test stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
