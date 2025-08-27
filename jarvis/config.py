"""
Configuración centralizada para JARVIS.

Este módulo proporciona una configuración tipada y validada para toda la aplicación,
utilizando Pydantic para la validación de tipos y valores.
"""

from typing import List, Optional, Literal, Dict, Any, Union, TypeVar, Type
from pathlib import Path
import os
import platform
import logging
from functools import lru_cache

from pydantic import Field, field_validator, root_validator, HttpUrl, AnyUrl
from pydantic_settings import BaseSettings

# Type variable for generic settings
T = TypeVar('T', bound='JarvisSettings')

# Configure logger
logger = logging.getLogger(__name__)


class JarvisSettings(BaseSettings):
    """
    Configuración principal de JARVIS.
    
    Esta clase define toda la configuración necesaria para el funcionamiento de JARVIS,
    con valores por defecto seguros y validación de tipos.
    """
    
    # Voice Configuration
    enable_voice: bool = Field(
        default=True,
        description="Habilitar/deshabilitar funcionalidad de voz"
    )
    
    voice_provider: Literal["pyttsx3"] = Field(
        default="pyttsx3",
        description="Proveedor de voz a utilizar"
    )
    
    voice_model: str = Field(
        default="",
        description="Modelo de voz a utilizar (depende del proveedor)"
    )
    
    voice_language: str = Field(
        default="es",
        description="Idioma predeterminado para la voz"
    )
    
    voice_commands: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Comandos de voz personalizados"
    )
    
    # STT (Speech-to-Text) Configuration
    stt_provider: Literal["whisper"] = Field(
        default="whisper",
        description="Proveedor de reconocimiento de voz"
    )
    
    # TTS (Text-to-Speech) Configuration
    tts_provider: Literal["pyttsx3"] = Field(
        default="pyttsx3",
        description="Proveedor de síntesis de voz"
    )
    
    # Whisper Configuration
    whisper_model: str = Field(
        default="base",
        description="Modelo de Whisper a utilizar (base, small, medium, large)"
    )
    
    whisper_device: str = Field(
        default="cpu",
        description="Dispositivo para ejecutar Whisper (cpu o cuda)"
    )
    
    # Agent Configuration
    agent_mode: Literal["local", "cloud", "hybrid"] = Field(
        default="hybrid",
        description="Modo de operación del agente"
    )
    
    agent_name: str = Field(
        default="JARVIS",
        description="Nombre del agente"
    )
    
    agent_language: Literal["es", "en"] = Field(
        default="es",
        description="Idioma principal del agente"
    )
    
    # LLM Configuration (LM Studio)
    llm_provider: Literal["lm_studio", "openai", "ollama"] = Field(
        default="lm_studio",
        description="Proveedor de modelo de lenguaje"
    )
    
    lm_studio_base_url: HttpUrl = Field(
        default="http://172.24.240.1:1234/v1/",
        description="URL base para la API de LM Studio (con la barra final)"
    )
    
    lm_studio_model: str = Field(
        default="local-model",
        description="Modelo de lenguaje a utilizar con LM Studio"
    )
    
    lm_studio_temperature: float = Field(
        default=0.7,
        description="Temperatura para la generación de texto (0-2)",
        ge=0.0,
        le=2.0
    )
    
    lm_studio_max_tokens: int = Field(
        default=2000,
        description="Número máximo de tokens a generar",
        gt=0
    )
    
    lm_studio_top_p: float = Field(
        default=0.9,
        description="Probabilidad acumulada para el muestreo (0-1)",
        ge=0.0,
        le=1.0
    )
    
    lm_studio_timeout: int = Field(
        default=300,
        description="Tiempo de espera para la API en segundos",
        gt=0
    )
    
    # Offline Mode
    offline_mode: bool = Field(
        default=True,
        description="Ejecutar en modo offline sin conexión a internet"
    )
    
    # Security Settings
    enable_code_execution: bool = Field(
        default=True,
        description="Permitir ejecución de código"
    )
    
    enable_system_commands: bool = False
    enable_file_operations: bool = True
    max_file_size_mb: int = Field(default=10, ge=1, le=100)
    allowed_directories: List[str] = Field(
        default=[
            str(Path.home() / "jarvis-workspace"),
            str(Path(os.environ.get("TEMP", "C:\\temp"))),
        ]
    )
    sandbox_type: Literal["docker", "restricted"] = "restricted"
    code_execution_timeout: int = Field(default=30, ge=5, le=300)
    max_memory_mb: int = Field(default=512, ge=64, le=2048)  # Aumentado para Windows
    
    # Cache
    redis_url: Optional[str] = None
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hora
    
    # Voice Command Patterns (default patterns for Spanish)
    voice_command_patterns: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "greeting": [
                r"hola\\b",
                r"buenos días\\b",
                r"buenas tardes\\b",
                r"buenas noches\\b",
                r"hey jarvis\\b",
                r"hola jarvis\\b"
            ],
            "farewell": [
                r"adivós\\b",
                r"hasta luego\\b",
                r"hasta pronto\\b",
                r"nos vemos\\b",
                r"hasta la próxima\\b"
            ],
            "help": [
                r"ayuda\\b",
                r"qué puedes hacer\\b",
                r"qué sabes hacer\\b",
                r"qué comandos hay\\b"
            ],
            "status": [
                r"cómo estás\\b",
                r"qué tal estás\\b",
                r"estás ahí\\b",
                r"estás funcionando\\b"
            ]
        }
    ) 
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: Literal["json", "text"] = "text"  # Cambiado a texto para mejor legibilidad en Windows
    log_file: str = str(Path("logs") / "jarvis.log")
    
    @field_validator('allowed_directories', mode='before')
    def validate_directories(cls, v):
        """Valida directorios permitidos."""
        if v is None:
            v = []
        elif isinstance(v, str):
            # Si es un string, asumir que es una lista separada por comas
            v = [d.strip() for d in v.split(',') if d.strip()]
        
        # Si no hay directorios, usar los valores por defecto
        if not v:
            v = [
                str(Path.home() / "jarvis-workspace"),
                str(Path(os.environ.get("TEMP", "C:\\temp"))),
            ]
        
        validated = []
        for directory in v:
            try:
                # Expandir variables de entorno en las rutas
                expanded = os.path.expandvars(directory)
                path = Path(expanded).absolute()
                # Crear el directorio si no existe
                path.mkdir(parents=True, exist_ok=True)
                validated.append(str(path))
            except Exception as e:
                print(f"Advertencia: No se pudo validar el directorio {directory}: {e}")
        
        # Asegurar al menos un directorio válido
        if not validated:
            default_dir = Path.home() / "jarvis-workspace"
            default_dir.mkdir(parents=True, exist_ok=True)
            validated = [str(default_dir)]
            
        return validated
    
    class Config:
        """Configuración de Pydantic para la clase de configuración."""
        
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        case_sensitive = False
        
        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            """Personaliza el orden de carga de las fuentes de configuración."""
            # 1. Valores por defecto
            # 2. Variables de entorno
            # 3. Archivo .env
            # 4. Argumentos de inicialización
            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )


@lru_cache(maxsize=1)
def get_settings() -> JarvisSettings:
    """
    Obtiene la configuración con caché para mejor rendimiento.
    
    Returns:
        JarvisSettings: Instancia de configuración de la aplicación.
        
    Example:
        >>> settings = get_settings()
        >>> print(settings.agent_name)
        'JARVIS'
    """
    try:
        settings = JarvisSettings()
        logger.debug("Configuración cargada exitosamente")
        return settings
    except Exception as e:
        logger.error(f"Error al cargar la configuración: {e}")
        # Retorna configuración por defecto en caso de error
        return JarvisSettings()

# Instancia global de configuración
settings = get_settings()

def ensure_directories() -> None:
    """
    Asegura que todos los directorios necesarios para la aplicación existan.
    
    Crea los directorios si no existen y verifica los permisos necesarios.
    """
    # Directorios base requeridos
    base_dirs = [
        "data",          # Datos de la aplicación
        "logs",          # Archivos de registro
        "cache",         # Caché de la aplicación
        "models",        # Modelos de IA descargados
        "config"         # Archivos de configuración adicionales
    ]
    
    for dir_name in base_dirs:
        try:
            dir_path = Path(dir_name)
            dir_path.mkdir(exist_ok=True, parents=True, mode=0o755)
            logger.debug(f"Directorio verificado: {dir_path.absolute()}")
        except OSError as e:
            logger.error(f"No se pudo crear el directorio {dir_name}: {e}")
            raise
    
    # Crear directorios permitidos
    for dir_path in settings.allowed_directories:
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

# Asegurar directorios al importar el módulo
ensure_directories()