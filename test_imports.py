# Test basic imports
print("Testing imports...")
try:
    from jarvis.config import JarvisSettings
    print("✅ JarvisSettings imported successfully")
    
    settings = JarvisSettings()
    print("✅ JarvisSettings instance created")
    
    from jarvis.simple_voice import SimpleVoiceAgent
    print("✅ SimpleVoiceAgent imported successfully")
    
    agent = SimpleVoiceAgent(settings)
    print("✅ SimpleVoiceAgent instance created")
    
    print("\n✅ All imports and instantiations successful!")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
