# -*- coding: utf-8 -*-
"""
core/agent.py — Core agent and application classes for JARVIS.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
import signal
import sys
import asyncio

from jarvis.utils.logger import get_logger, setup_logging
from jarvis.tools.registry import ToolRegistry
from jarvis.tools.system_info import SystemInfoTool
from jarvis.providers.factory import LLMProviderFactory
from jarvis.security.validator import SecurityValidator
from jarvis.security.sandbox import WindowsSandbox
from jarvis.config import JarvisSettings, get_settings

# Set up logger
log = get_logger(__name__)

class Agent:
    """Base agent class for handling provider and tool interactions."""
    def __init__(self, provider, session):
        self.provider = provider
        self.session = session
        self.tools = ToolRegistry.default_registry()

    def respond(self, prompt: str) -> str:
        """Handle a user prompt and generate a response."""
        if prompt.startswith("!"):
            return self._handle_tool_command(prompt[1:].strip())


class JarvisAgent:
    """Main JARVIS agent for Windows."""
    
    def __init__(self, settings: JarvisSettings):
        self.settings = settings
        self.llm_provider = None
        self.sandbox = None
        self.validator = None
        self.system_tool = None
        self.voice_agent = None
        self.conversation_history = []
        self.is_initialized = False
        self.session_stats = {
            'requests': 0,
            'successful_executions': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        self.tools = ToolRegistry.default_registry(self.settings)
        self.voice_command_recognizer = None
        self.voice_response_formatter = None
    
    async def initialize(self):
        """Initialize JARVIS components."""
        try:
            log.info("🚀 Initializing JARVIS v2.0")
            
            # Initialize voice agent if enabled
            if hasattr(self.settings, 'enable_voice') and self.settings.enable_voice:
                log.info("🔊 Initializing voice module...")
                try:
                    from jarvis.voice_agent import VoiceJarvisAgent
                    self.voice_agent = VoiceJarvisAgent(self.settings)
                    await self.voice_agent.initialize()
                    log.info("✅ Voice module initialized")
                except ImportError as e:
                    log.warning(f"Voice module not available: {e}")
            
            # Initialize LLM provider
            self.llm_provider = await LLMProviderFactory.create(settings=self.settings)
            
            await self.llm_provider.initialize()
            
            # Initialize security tools if code execution is enabled
            if hasattr(self.settings, 'enable_code_execution') and self.settings.enable_code_execution:
                self.sandbox = WindowsSandbox(self.settings)
                self.validator = SecurityValidator(self.settings)
                log.info("✅ Code sandbox enabled")
            
            # Initialize system tools
            await self._initialize_tools()
            
            self.is_initialized = True
            log.info("✅ JARVIS initialized successfully")
            
        except Exception as e:
            log.error(f"❌ Error initializing JARVIS: {e}", exc_info=True)
            raise RuntimeError(f"Initialization error: {e}")
    
    async def _initialize_tools(self):
        """Initialize available tools."""
        self.system_tool = SystemInfoTool(self.settings)
        # Add other tool initializations here
    
    async def cleanup(self):
        """Clean up resources."""
        if self.voice_agent:
            await self.voice_agent.cleanup()
        if self.llm_provider:
            await self.llm_provider.cleanup()

    def _handle_tool_command(self, cmd: str) -> str:
        # Formato: !nombre_tool arg1 arg2 ...
        parts = cmd.split()
        if not parts:
            return "Comando de herramienta vacío."
        name, *args = parts
        tool = self.tools.get(name) # Changed self.agent.tools to self.tools
        if not tool:
            return f"Herramienta '{name}' no encontrada. Usa !help para ver opciones."
        try:
            return tool.run(*args)
        except TypeError:
            return tool.help()
        except Exception as e:
            log.exception("Error al ejecutar herramienta %s", name)
            return f"Error en herramienta '{name}': {e}"

    async def process_message(self, user_input: str) -> str:
        """Process user input and generate a response."""
        self.session_stats['requests'] += 1
        
        if user_input.startswith("!"):
            # Handle tool commands
            return self._handle_tool_command(user_input[1:].strip())
        
        # Otherwise, send to LLM
        try:
            response = await self.llm_provider.generate(user_input)
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": response})
            self.session_stats['successful_executions'] += 1
            return response
        except Exception as e:
            self.session_stats['errors'] += 1
            log.error(f"Error generating response from LLM: {e}", exc_info=True)
            return f"Lo siento, hubo un error al procesar tu solicitud: {str(e)}"


class JarvisApplication:
    """Main JARVIS application class."""
    
    def __init__(self):
        self.settings = None
        self.agent = None
        self.is_running = False
    
    async def initialize(self):
        """Initialize the application."""
        try:
            # Load settings
            self.settings = get_settings()
            
            # Set up logging
            setup_logging(self.settings)
            
            # Initialize agent
            self.agent = JarvisAgent(self.settings)
            await self.agent.initialize()
            
            # Set up signal handlers
            signal.signal(signal.SIGINT, self._handle_shutdown)
            signal.signal(signal.SIGTERM, self._handle_shutdown)
            
            self.is_running = True
            
        except Exception as e:
            log.error(f"Failed to initialize application: {e}", exc_info=True)
            raise
    
    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals."""
        log.info("Shutdown signal received...")
        self.is_running = False
    
    async def cleanup(self):
        """Clean up resources."""
        if self.agent:
            await self.agent.cleanup()
    
    async def __aenter__(self):
        """Context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.cleanup()
        return None

    
