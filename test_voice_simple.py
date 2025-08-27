"""Simple test script for voice commands."""
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleVoiceAgent:
    """A simple voice agent for testing."""
    
    def __init__(self):
        self.voice_commands = {
            "hola": self._handle_greeting,
            "adiós": self._handle_goodbye,
            "ayuda": self._handle_help,
            "estado": self._handle_status,
        }
    
    async def initialize(self):
        """Initialize the voice agent."""
        logger.info("Initializing SimpleVoiceAgent...")
        return True
    
    async def process_text_command(self, text: str) -> str:
        """Process a text command and return a response."""
        text = text.lower().strip()
        
        # Check for exact matches first
        if text in self.voice_commands:
            return await self.voice_commands[text]()
        
        # Check for partial matches
        for cmd, handler in self.voice_commands.items():
            if cmd in text:
                return await handler()
        
        # No command matched
        return "No entiendo el comando. Prueba con 'ayuda' para ver los comandos disponibles."
    
    # Command handlers
    async def _handle_greeting(self) -> str:
        return "¡Hola! Soy JARVIS, tu asistente de voz. ¿En qué puedo ayudarte hoy?"
    
    async def _handle_goodbye(self) -> str:
        return "¡Hasta luego! Si necesitas algo más, aquí estaré."
    
    async def _handle_help(self) -> str:
        commands = ", ".join(f"'{cmd}'" for cmd in self.voice_commands.keys())
        return f"Puedes decirme: {commands}. O simplemente hazme una pregunta."
    
    async def _handle_status(self) -> str:
        return "Estoy funcionando correctamente. ¿En qué puedo ayudarte?"

async def main():
    """Main test function."""
    print("🚀 Iniciando prueba de comandos de voz...")
    
    # Create and initialize the voice agent
    agent = SimpleVoiceAgent()
    await agent.initialize()
    
    # Test commands with various patterns
    test_commands = [
        "hola",
        "buenos días jarvis",
        "oye jarvis, ¿qué tal estás?",
        "necesito ayuda con algo",
        "¿qué puedes hacer?",
        "dime qué comandos hay disponibles",
        "¿estás funcionando bien?",
        "estás ahí?",
        "hasta luego, nos vemos mañana",
        "chao jarvis"
    ]
    
    # Process each test command
    for cmd in test_commands:
        print(f"\nTú: {cmd}")
        response = await agent.process_text_command(cmd)
        print(f"JARVIS: {response}")
        await asyncio.sleep(1)  # Small delay between commands
    
    print("\n✅ Prueba completada exitosamente!")

if __name__ == "__main__":
    asyncio.run(main())
