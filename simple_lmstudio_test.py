import aiohttp
import asyncio

async def test_connection():
    url = "http://localhost:1234/v1/models"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    print("✅ Successfully connected to LM Studio!")
                    print(f"Status: {response.status}")
                    print("Response:", await response.text())
                else:
                    print(f"❌ Error: Server returned status {response.status}")
    except aiohttp.ClientConnectorError:
        print("❌ Could not connect to LM Studio. Please check if it's running and the server is enabled.")
    except asyncio.TimeoutError:
        print("❌ Connection timed out. Is LM Studio running?")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    print("Testing LM Studio connection...")
    asyncio.run(test_connection())
