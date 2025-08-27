from jarvis.providers.lm_studio import LMStudioProvider
import asyncio

async def test():
    provider = LMStudioProvider()
    try:
        response = await provider.generate("Hola, ¿cómo estás?")
        print(response)
    finally:
        await provider.close()

if __name__ == "__main__":
    asyncio.run(test())