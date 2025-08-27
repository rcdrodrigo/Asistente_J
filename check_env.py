"""Check if LiveKit environment variables are properly set."""
import os
from dotenv import load_dotenv

def check_livekit_config():
    """Check if LiveKit environment variables are set."""
    load_dotenv()
    
    required_vars = [
        "LIVEKIT_URL",
        "LIVEKIT_API_KEY",
        "LIVEKIT_API_SECRET",
        "STT_PROVIDER",
        "TTS_PROVIDER"
    ]
    
    print("🔍 Verificando configuración de LiveKit...\n")
    
    all_ok = True
    for var in required_vars:
        value = os.getenv(var)
        status = "✅" if value else "❌"
        print(f"{status} {var}: {'*****' if 'KEY' in var or 'SECRET' in var else value or 'No configurado'}")
        if not value:
            all_ok = False
    
    # Check STT provider specific variables
    stt_provider = os.getenv("STT_PROVIDER", "").lower()
    if stt_provider == "deepgram" and not os.getenv("DEEPGRAM_API_KEY"):
        print("❌ DEEPGRAM_API_KEY no está configurado para el proveedor STT")
        all_ok = False
    
    # Check TTS provider specific variables
    tts_provider = os.getenv("TTS_PROVIDER", "").lower()
    if tts_provider == "elevenlabs" and not os.getenv("ELEVENLABS_API_KEY"):
        print("❌ ELEVENLABS_API_KEY no está configurado para el proveedor TTS")
        all_ok = False
    elif tts_provider == "cartesia" and not os.getenv("CARTESIA_API_KEY"):
        print("❌ CARTESIA_API_KEY no está configurado para el proveedor TTS")
        all_ok = False
    
    if all_ok:
        print("\n✅ ¡Todas las variables de entorno necesarias están configuradas correctamente!")
        print("Puedes ejecutar las pruebas de integración con LiveKit.")
    else:
        print("\n❌ Faltan algunas configuraciones necesarias.")
        print("Por favor, asegúrate de configurar todas las variables de entorno requeridas.")
        print("Consulta el archivo .env.example para ver un ejemplo de configuración.")

if __name__ == "__main__":
    check_livekit_config()
