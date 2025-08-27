"""Voice-optimized tools for JARVIS."""
from typing import Dict, Any, Optional, List, Union
import re
import json
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class VoiceCommandType(Enum):
    """Types of voice commands that can be recognized."""
    GREETING = "greeting"
    FAREWELL = "farewell"
    HELP = "help"
    STATUS = "status"
    QUERY = "query"
    COMMAND = "command"
    CONFIRMATION = "confirmation"
    REJECTION = "rejection"


@dataclass
class VoiceCommand:
    """Represents a recognized voice command."""
    type: VoiceCommandType
    text: str
    confidence: float = 1.0
    parameters: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert command to dictionary."""
        return {
            "type": self.type.value,
            "text": self.text,
            "confidence": self.confidence,
            "parameters": self.parameters or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VoiceCommand':
        """Create command from dictionary."""
        return cls(
            type=VoiceCommandType(data["type"]),
            text=data["text"],
            confidence=data.get("confidence", 1.0),
            parameters=data.get("parameters", {})
        )


class VoiceCommandRecognizer:
    """Recognizes voice commands from text input."""
    
    def __init__(self):
        self.patterns = {
            VoiceCommandType.GREETING: [
                r"hola\b",
                r"buenos días\b",
                r"buenas tardes\b",
                r"buenas noches\b",
                r"hey jarvis\b",
                r"hola jarvis\b"
            ],
            VoiceCommandType.FAREWELL: [
                r"adi[óo]s\b",
                r"hasta luego\b",
                r"hasta pronto\b",
                r"nos vemos\b",
                r"hasta la próxima\b"
            ],
            VoiceCommandType.HELP: [
                r"ayuda\b",
                r"qué puedes hacer\b",
                r"qué sabes hacer\b",
                r"qué comandos hay\b"
            ],
            VoiceCommandType.STATUS: [
                r"cómo estás\b",
                r"qué tal estás\b",
                r"estás ahí\b",
                r"estás funcionando\b"
            ]
        }
        self.command_handlers = {
            VoiceCommandType.GREETING: self._handle_greeting,
            VoiceCommandType.FAREWELL: self._handle_farewell,
            VoiceCommandType.HELP: self._handle_help,
            VoiceCommandType.STATUS: self._handle_status,
        }
    
    def recognize(self, text: str) -> Optional[VoiceCommand]:
        """Recognize a voice command from text."""
        if not text or not isinstance(text, str):
            return None
            
        text = text.lower().strip()
        
        # Check for exact matches first
        for cmd_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return VoiceCommand(
                        type=cmd_type,
                        text=text,
                        confidence=1.0
                    )
        
        # No command recognized
        return VoiceCommand(
            type=VoiceCommandType.QUERY,
            text=text,
            confidence=0.0
        )
    
    async def execute_command(self, command: VoiceCommand, context: Dict[str, Any] = None) -> str:
        """Execute a recognized voice command."""
        context = context or {}
        handler = self.command_handlers.get(command.type)
        if handler:
            return await handler(command, context)
        
        # Default response for unhandled commands
        return f"No entiendo el comando: {command.text}"
    
    async def _handle_greeting(self, command: VoiceCommand, context: Dict[str, Any]) -> str:
        """Handle greeting command."""
        greetings = [
            "¡Hola! ¿En qué puedo ayudarte hoy?",
            "¡Hola! ¿Qué necesitas?",
            "¡Hola! Soy JARVIS, tu asistente. ¿En qué puedo ayudarte?"
        ]
        import random
        return random.choice(greetings)
    
    async def _handle_farewell(self, command: VoiceCommand, context: Dict[str, Any]) -> str:
        """Handle farewell command."""
        farewells = [
            "¡Hasta luego! Si necesitas algo más, aquí estaré.",
            "¡Adiós! Fue un placer ayudarte.",
            "¡Hasta pronto!"
        ]
        import random
        return random.choice(farewells)
    
    async def _handle_help(self, command: VoiceCommand, context: Dict[str, Any]) -> str:
        """Handle help command."""
        return (
            "Puedo ayudarte con varias tareas. Puedes decirme cosas como:\n"
            "- 'Hola' para saludar\n"
            "- '¿Qué puedes hacer?' para ver mis capacidades\n"
            "- 'Busca información sobre...' para buscar en internet\n"
            "- 'Abre el archivo...' para ver el contenido de un archivo\n"
            "- '¿Qué hora es?' para saber la hora actual\n"
            "- 'Adiós' para terminar la conversación"
        )
    
    async def _handle_status(self, command: VoiceCommand, context: Dict[str, Any]) -> str:
        """Handle status command."""
        from datetime import datetime
        now = datetime.now()
        return f"Estoy funcionando correctamente. Son las {now.hour} y {now.minute} minutos."


class VoiceResponseFormatter:
    """Formats responses for voice output."""
    
    @staticmethod
    def format_response(response: Any) -> str:
        """Format a response for voice output."""
        if response is None:
            return "No tengo una respuesta para eso."
            
        if isinstance(response, str):
            return VoiceResponseFormatter._clean_text(response)
            
        if isinstance(response, (dict, list)):
            return VoiceResponseFormatter._format_structured_data(response)
            
        return str(response)
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean text for voice output."""
        # Remove markdown and special characters
        text = re.sub(r'[#*_`\[\]]', '', text)
        
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Remove multiple spaces and newlines
        text = ' '.join(text.split())
        
        return text.strip()
    
    @staticmethod
    def _format_structured_data(data: Union[dict, list], level: int = 0) -> str:
        """Format structured data as a readable string."""
        if isinstance(data, list):
            if not data:
                return "No hay elementos para mostrar."
                
            if len(data) == 1:
                return VoiceResponseFormatter._format_structured_data(data[0], level)
                
            items = [f"{i+1}. {VoiceResponseFormatter._format_structured_data(item, level+1)}" 
                    for i, item in enumerate(data)]
            return "\n".join(items)
            
        if isinstance(data, dict):
            if not data:
                return "No hay información disponible."
                
            items = []
            for key, value in data.items():
                formatted_key = key.replace('_', ' ').title()
                formatted_value = VoiceResponseFormatter._format_structured_data(value, level+1)
                
                if isinstance(value, (dict, list)) and level < 2:  # Limit nesting
                    items.append(f"{formatted_key}: {formatted_value}")
                else:
                    items.append(f"{formatted_key}: {formatted_value}")
                    
            if level == 0:
                return "\n".join(items)
            return ", ".join(items)
            
        return str(data)
