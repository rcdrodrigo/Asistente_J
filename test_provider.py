import asyncio
import logging
from jarvis.providers.lm_studio import LMStudioProvider, LMStudioConfig, GenerationConfig
from jarvis.providers.base import ChatMessage

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

async def test_provider():
    # Configuración personalizada (opcional)
    config = LMStudioConfig(
        base_url="http://172.24.240.1:1234/v1",
        model="local-model",
        timeout=60
    )
    
    # Crear instancia del proveedor
    provider = LMStudioProvider(config)
    
    try:
        # Probar generación simple
        print("\n--- Probando generación simple ---")
        response = await provider.generate("Hola, ¿cómo estás?")
        print(f"Respuesta: {response}")
        
        # Probar chat completion
        print("\n--- Probando chat completion ---")
        messages = [
            ChatMessage(role="system", content="Eres un asistente útil."),
            ChatMessage(role="user", content="¿Qué puedes hacer?")
        ]
        response = await provider.chat_completion(messages)
        for msg in response:
            print(f"{msg.role.upper()}: {msg.content}")
            
    finally:
        await provider.close()

if __name__ == "__main__":
    asyncio.run(test_provider())