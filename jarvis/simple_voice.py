"""A simplified voice interface for JARVIS."""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable, Awaitable

from .config import JarvisSettings

logger = logging.getLogger(__name__)

class SimpleVoiceAgent:
    """A simplified voice agent that can be extended with actual voice capabilities."""
    
    def __init__(self, settings: JarvisSettings):
        self.settings = settings
        self.voice_commands = self._setup_voice_commands()
        self.command_patterns = self._setup_command_patterns()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def initialize(self) -> bool:
        """Initialize the voice agent."""
        logger.info("Initializing SimpleVoiceAgent...")
        return True
    
    def _setup_command_patterns(self) -> Dict[str, List[str]]:
        """Set up command patterns for more flexible matching."""
        return {
            "saludo": ["hola", "buenos días", "buenas tardes", "buenas noches", "hey jarvis"],
            "despedida": ["adiós", "hasta luego", "hasta pronto", "nos vemos", "chao"],
            "ayuda": ["ayuda", "qué puedes hacer", "qué comandos hay", "qué sabes hacer"],
            "estado": ["cómo estás", "qué tal estás", "estás ahí", "estás funcionando"],
        }
    
    def _setup_voice_commands(self) -> Dict[str, Callable[[], Awaitable[str]]]:
        """Set up the available voice commands."""
        return {
            "saludo": self._handle_greeting,
            "despedida": self._handle_goodbye,
            "ayuda": self._handle_help,
            "estado": self._handle_status,
        }
    
    async def process_text_command(self, text: str) -> str:
        """Process a text command and return a response."""
        if not text or not isinstance(text, str):
            return "No he recibido ningún comando. ¿Puedes repetir?"
            
        text = text.lower().strip()
        
        # Check for command patterns
        for cmd_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    handler = self.voice_commands.get(cmd_type)
                    if handler:
                        return await handler()
        
        # Check for exact matches as fallback
        for cmd, handler in self.voice_commands.items():
            if cmd in text:
                return await handler()
        
        # No command matched
        return "No entiendo el comando. Di 'ayuda' para ver lo que puedo hacer."
    
    async def _handle_greeting(self) -> str:
        """Handle greeting command."""
        return "¡Hola! Soy JARVIS, tu asistente de voz. ¿En qué puedo ayudarte hoy?"
    
    async def _handle_goodbye(self) -> str:
        """Handle goodbye command."""
        return "¡Hasta luego! Si necesitas algo más, aquí estaré."
    
    async def _handle_help(self) -> str:
        """Handle help command."""
        help_text = ["Puedes decirme cosas como:"]
        for cmd_type, patterns in self.command_patterns.items():
            examples = ", ".join(f"'{p}'" for p in patterns[:2])  # Show first 2 examples
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
        """Handle status command."""
        return "Estoy funcionando correctamente. ¿En qué puedo ayudarte?"
    
    async def _handle_general_query(self, query: str) -> str:
        """Handle general queries."""
        return f"He recibido tu consulta: {query}. Esta funcionalidad estará disponible pronto."


async def test_voice_agent():
    """Test the simple voice agent."""
    settings = JarvisSettings()
    agent = SimpleVoiceAgent(settings)
    await agent.initialize()
    
    test_commands = [
        "hola",
        "¿cómo estás?",
        "ayuda",
        "adiós"
    ]
    
    for cmd in test_commands:
        print(f"Tú: {cmd}")
        response = await agent.process_text_command(cmd)
        print(f"JARVIS: {response}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_voice_agent())
