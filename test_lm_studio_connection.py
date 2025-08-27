"""
Test script to verify LM Studio connection and basic functionality.
"""
import asyncio
import aiohttp
import json

async def test_lmstudio():
    """Test connection to LM Studio and basic completion."""
    url = "http://localhost:1234/v1/chat/completions"
    
    # Test prompt
    messages = [
        {"role": "system", "content": "Eres un asistente útil que responde en español."},
        {"role": "user", "content": "Dime algo interesante sobre la inteligencia artificial."}
    ]
    
    payload = {
        "model": "local-model",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        print("🔍 Probando conexión con LM Studio...")
        print(f"URL: {url}")
        print("Enviando solicitud...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=30) as response:
                print(f"\n📡 Estado de la respuesta: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ ¡Conexión exitosa!")
                    print("\n📝 Respuesta del modelo:")
                    if 'choices' in result and len(result['choices']) > 0:
                        message = result['choices'][0].get('message', {})
                        print(message.get('content', 'No se pudo obtener el contenido de la respuesta'))
                    else:
                        print("Estructura de respuesta inesperada:")
                        print(json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    print(f"❌ Error en la respuesta: {response.status}")
                    print("Detalles:", await response.text())
                    
    except aiohttp.ClientConnectorError:
        print("❌ No se pudo conectar al servidor LM Studio.")
        print("Por favor verifica que:")
        print("1. LM Studio esté en ejecución")
        print("2. El servidor local esté habilitado en la pestaña 'Local Server'")
        print("3. El puerto 1234 esté configurado correctamente")
    except asyncio.TimeoutError:
        print("❌ Tiempo de espera agotado. El servidor no respondió a tiempo.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🛠️  Probando integración con LM Studio")
    print("=" * 50)
    asyncio.run(test_lmstudio())
    input("\nPresiona Enter para salir...")
