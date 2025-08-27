"""
Manual test for LM Studio provider.
Run this script after starting LM Studio with the local server enabled.
"""
import asyncio
import aiohttp
import json

async def test_lmstudio():
    # LM Studio API endpoint
    url = "http://localhost:1234/v1/chat/completions"
    
    # Test prompt
    messages = [
        {"role": "system", "content": "Eres un asistente útil."},
        {"role": "user", "content": "Dime algo interesante sobre la inteligencia artificial"}
    ]
    
    # Request payload
    payload = {
        "model": "local-model",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 100,
        "stream": False
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("Sending request to LM Studio...")
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=30) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    print("\nResponse:")
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    print(f"Error: {await response.text()}")
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure LM Studio is running with the local server enabled:")
        print("1. Open LM Studio")
        print("2. Go to 'Local Server' tab")
        print("3. Toggle 'Server' ON")
        print("4. Make sure it's set to listen on http://localhost:1234")

if __name__ == "__main__":
    print("LM Studio Manual Test")
    print("====================")
    asyncio.run(test_lmstudio())
