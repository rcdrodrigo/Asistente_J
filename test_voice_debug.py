"""Debug script for voice commands with detailed logging."""
import asyncio
import logging
import sys

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

class SimpleVoiceAgent:
    """A simple voice agent for testing with detailed logging."""
    
    def __init__(self):
        logger.debug("Initializing SimpleVoiceAgent...")
        self.voice_commands = self._setup_voice_commands()
        self.command_patterns = self._setup_command_patterns()
        logger.debug("Voice agent initialized")
    
    async def initialize(self):
        """Initialize the voice agent."""
        logger.info("Initializing voice agent...")
        return True
    
    def _setup_command_patterns(self) -> dict:
        """Set up command patterns for flexible matching."""
        logger.debug("Setting up command patterns...")
        patterns = {
            "saludo": ["hola", "buenos días", "buenas tardes", "buenas noches", "hey jarvis"],
            "despedida": ["adiós", "hasta luego", "hasta pronto", "nos vemos", "chao"],
            "ayuda": ["ayuda", "qué puedes hacer", "qué comandos hay", "qué sabes hacer"],
            "estado": ["cómo estás", "qué tal estás", "estás ahí", "estás funcionando"],
        }
        logger.debug(f"Command patterns set up: {list(patterns.keys())}")
        return patterns
    
    def _setup_voice_commands(self) -> dict:
        """Set up the available voice commands."""
        logger.debug("Setting up voice commands...")
        commands = {
            "saludo": self._handle_greeting,
            "despedida": self._handle_goodbye,
            "ayuda": self._handle_help,
            "estado": self._handle_status,
        }
        logger.debug(f"Voice commands set up: {list(commands.keys())}")
        return commands
    
    async def process_text_command(self, text: str) -> str:
        """Process a text command and return a response."""
        logger.debug(f"Processing command: {text}")
        
        if not text or not isinstance(text, str):
            logger.warning("Received empty or invalid command")
            return "No he recibido ningún comando. ¿Puedes repetir?"
            
        text = text.lower().strip()
        logger.debug(f"Normalized command: {text}")
        
        # Check for command patterns
        for cmd_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    logger.debug(f"Matched pattern '{pattern}' for command type '{cmd_type}'")
                    handler = self.voice_commands.get(cmd_type)
                    if handler:
                        logger.debug(f"Found handler for command type: {cmd_type}")
                        return await handler()
        
        # Check for exact matches as fallback
        for cmd, handler in self.voice_commands.items():
            if cmd in text:
                logger.debug(f"Matched exact command: {cmd}")
                return await handler()
        
        # No command matched
        logger.debug("No matching command found")
        return "No entiendo el comando. Di 'ayuda' para ver lo que puedo hacer."
    
    # Command handlers
    async def _handle_greeting(self) -> str:
        logger.debug("Handling greeting command")
        return "¡Hola! Soy JARVIS, tu asistente de voz. ¿En qué puedo ayudarte hoy?"
    
    async def _handle_goodbye(self) -> str:
        logger.debug("Handling goodbye command")
        return "¡Hasta luego! Si necesitas algo más, aquí estaré."
    
    async def _handle_help(self) -> str:
        logger.debug("Handling help command")
        help_text = ["Puedes decirme cosas como:"]
        for cmd_type, patterns in self.command_patterns.items():
            examples = ", ".join(f"'{p}'" for p in patterns[:2])
            help_text.append(f"- {examples} ({self._get_command_description(cmd_type)})")
        help_text.append("O simplemente hazme una pregunta.")
        return "\n".join(help_text)
    
    def _get_command_description(self, cmd_type: str) -> str:
        """Get a description for a command type."""
        descriptions = {
            "saludo": "para saludarme",
            "despedida": "para despedirte",
            "ayuda": "para ver esta ayuda",
            "estado": "para ver mi estado"
        }
        return descriptions.get(cmd_type, "")
    
    async def _handle_status(self) -> str:
        logger.debug("Handling status command")
        return "Estoy funcionando correctamente. ¿En qué puedo ayudarte?"

async def main():
    """Main test function with detailed logging."""
    print("🚀 Iniciando prueba de comandos de voz con depuración...\n")
    
    # Create and initialize the voice agent
    logger.info("Creando agente de voz...")
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
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n--- Comando {i}/{len(test_commands)} ---")
        print(f"Tú: {cmd}")
        response = await agent.process_text_command(cmd)
        print(f"JARVIS: {response}")
        await asyncio.sleep(0.5)  # Small delay between commands
    
    print("\n✅ Prueba completada exitosamente!")

if __name__ == "__main__":
    asyncio.run(main())
