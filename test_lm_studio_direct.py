"""
Direct test of LM Studio provider without package installation.
"""
import asyncio
import sys
import os
import aiohttp
from pathlib import Path

# Add the jarvis directory to Python path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

# Now import the LM Studio provider
from jarvis.providers.lm_studio import LMStudioProvider, LMStudioConfig, GenerationConfig
from jarvis.providers.base import ChatMessage

async def test_lm_studio():
    """Test LM Studio provider with direct instantiation."""
    provider = None
    try:
        print("Testing LM Studio provider...")
        
        # Create config with default values
        config = LMStudioConfig(
            base_url="http://localhost:1234/v1",  # Changed to localhost
            model="local-model",
            temperature=0.7,
            max_tokens=2000,
            top_p=0.9,
            timeout=30  # Reduced timeout for faster failure
        )
        
        print(f"Using config: {config}")
        
        # Create provider
        provider = LMStudioProvider(config)
        print("LM Studio provider created successfully")
        
        # Test connection
        print("\nTesting connection to LM Studio...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:1234/v1/models") as response:
                    if response.status == 200:
                        models = await response.json()
                        print(f"Connected to LM Studio. Available models: {models}")
                    else:
                        print(f"Error connecting to LM Studio. Status: {response.status}")
                        print("Please make sure LM Studio is running with the server enabled.")
                        return
        except Exception as e:
            print(f"Error connecting to LM Studio: {e}")
            print("Please make sure LM Studio is running with the server enabled.")
            return
        
        # Test simple completion
        prompt = "Escribe un breve poema sobre la inteligencia artificial"
        print(f"\nTesting completion with prompt: {prompt}")
        
        gen_config = GenerationConfig(
            temperature=0.8,
            max_tokens=100,
            top_p=0.9,
            stream=False
        )
        
        response = await provider.generate(
            prompt=prompt,
            config=gen_config
        )
        
        print("\nResponse received:")
        print("-" * 80)
        print(response)
        print("-" * 80)
        
        # Test chat completion
        print("\nTesting chat completion...")
        messages = [
            ChatMessage(role="system", content="Eres un asistente útil en español."),
            ChatMessage(role="user", content="¿Qué puedes contarme sobre la inteligencia artificial?")
        ]
        
        chat_response = await provider.chat_completion(
            messages=messages,
            config=gen_config
        )
        
        print("\nChat response received:")
        print("-" * 80)
        print(chat_response)
        print("-" * 80)
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"Error during LM Studio test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if provider is not None:
            await provider.close()  # Make sure to await the close coroutine

if __name__ == "__main__":
    asyncio.run(test_lm_studio())
