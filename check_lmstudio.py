import aiohttp
import asyncio

async def check_lmstudio():
    url = "http://localhost:1234/v1/models"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    response_text = await response.text()
                    print(f"✅ LM Studio server is running and accessible\n"
                          f"Status: {response.status}\n"
                          f"Response: {response_text}")
                else:
                    print(f"❌ LM Studio server returned status: {response.status}")
    except aiohttp.ClientConnectorError:
        print("❌ Could not connect to LM Studio server. Please ensure:")
        print("1. LM Studio is running")
        print("2. The local server is enabled in LM Studio")
        print("3. The server is configured to listen on http://localhost:1234")
        print("\nTo enable the server in LM Studio:")
        print("1. Go to the 'Local Server' tab")
        print("2. Make sure 'Server' is toggled ON")
        print("3. Verify the URL matches: http://localhost:1234")
    except asyncio.TimeoutError:
        print("❌ Connection to LM Studio timed out. The server might be running but not responding.")
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_lmstudio())
