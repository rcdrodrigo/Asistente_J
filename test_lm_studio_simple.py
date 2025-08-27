"""
Simple test script for LM Studio provider.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from jarvis.providers.lm_studio import LMStudioProvider, LMStudioConfig

async def test_lm_studio():
    """Test LM Studio provider with direct instantiation."""
    try:
        print("Testing LM Studio provider...")
        
        # Create config with default values
        config = LMStudioConfig()
        print(f"Using config: {config}")
        
        # Create provider
        provider = LMStudioProvider(config)
        print("LM Studio provider created successfully")
        
        # Test simple completion
        prompt = "Escribe un breve poema sobre la inteligencia artificial"
        print(f"\nTesting completion with prompt: {prompt}")
        
        response = await provider.generate(
            prompt=prompt,
            max_tokens=100,
            temperature=0.8
        )
        
        print("\nResponse received:")
        print("-" * 80)
        print(response)
        print("-" * 80)
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Error during LM Studio test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_lm_studio())
