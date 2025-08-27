"""
Test script to verify LM Studio provider integration.
"""
import asyncio
import logging
from jarvis.config import JarvisSettings
from jarvis.providers.factory import LLMProviderFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_lm_studio():
    """Test LM Studio provider with current configuration."""
    try:
        # Load settings
        settings = JarvisSettings()
        logger.info("Testing LM Studio provider with settings:")
        logger.info(f"  Base URL: {settings.lm_studio_base_url}")
        logger.info(f"  Model: {settings.lm_studio_model}")
        logger.info(f"  Temperature: {settings.lm_studio_temperature}")
        logger.info(f"  Max Tokens: {settings.lm_studio_max_tokens}")
        
        # Create provider
        provider = await LLMProviderFactory.create("lm_studio", settings)
        logger.info("LM Studio provider created successfully")
        
        # Test simple completion
        prompt = "Escribe un breve poema sobre la inteligencia artificial"
        logger.info(f"Testing completion with prompt: {prompt}")
        
        response = await provider.generate(
            prompt=prompt,
            max_tokens=100,
            temperature=0.8
        )
        
        logger.info("\nResponse received:")
        print("-" * 80)
        print(response)
        print("-" * 80)
        
        # Test chat completion
        messages = [
            {"role": "system", "content": "Eres un asistente útil en español."},
            {"role": "user", "content": "¿Qué puedes contarme sobre la inteligencia artificial?"}
        ]
        
        logger.info("\nTesting chat completion...")
        chat_response = await provider.chat(
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        
        logger.info("\nChat response received:")
        print("-" * 80)
        print(chat_response)
        print("-" * 80)
        
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during LM Studio test: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(test_lm_studio())
