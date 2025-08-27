import aiohttp
import asyncio
import json

async def test_connection():
    url = "http://172.24.240.1:1234/v1/chat/completions"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "model": "local-model",
        "messages": [{"role": "user", "content": "Hola"}],
        "temperature": 0.7
    }
    
    print(f"Enviando petición a: {url}")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                print(f"Status: {response.status}")
                print("Headers de respuesta:")
                for k, v in response.headers.items():
                    print(f"  {k}: {v}")
                
                text = await response.text()
                print("\nRespuesta completa:")
                print(text)
                
    except Exception as e:
        print(f"\nError en la petición: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_connection())
