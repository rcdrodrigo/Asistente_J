"""Factory para crear proveedores LLM."""

from typing import Optional, Dict, Type, Any, Union
from .base import LLMProvider
from .lm_studio import LMStudioProvider, LMStudioConfig
from .openai import OpenAIProvider, OpenAIConfig
from ..config import JarvisSettings
from ..utils.logger import get_logger

logger = get_logger(__name__)

class LLMProviderFactory:
    """Factory para crear proveedores LLM según configuración."""
    
    _providers: Dict[str, Type[LLMProvider]] = {
        'lm_studio': LMStudioProvider,
        'openai': OpenAIProvider,
        # Add other providers as needed
    }
    
    @classmethod
    async def create(cls, provider_name: Optional[str] = None, 
                    settings: Optional[JarvisSettings] = None) -> LLMProvider:
        """Crea un proveedor LLM basado en la configuración.
        
        Args:
            provider_name: Nombre del proveedor a crear. Si es None, se usa el de la configuración.
            settings: Configuración de la aplicación. Si es None, se cargan los ajustes por defecto.
            
        Returns:
            Instancia del proveedor LLM configurado.
            
        Raises:
            ValueError: Si el proveedor no existe o la configuración es inválida.
        """
        settings = settings or JarvisSettings()
        provider_name = provider_name or settings.llm_provider
        
        if provider_name not in cls._providers:
            raise ValueError(f"Proveedor no soportado: {provider_name}")
            
        provider_class = cls._providers[provider_name]
        
        # Configuración específica del proveedor
        if provider_name == 'lm_studio':
            return await cls._create_lmstudio_provider(settings)
        elif provider_name == 'openai':
            return await cls._create_openai_provider(settings)
        else:
            # Para proveedores sin configuración especial
            return provider_class()
    
    @classmethod
    async def _create_lmstudio_provider(cls, settings: JarvisSettings) -> LMStudioProvider:
        """Crea y configura el proveedor LM Studio."""
        # Usa el método from_settings de LMStudioConfig para crear la configuración
        return LMStudioProvider(settings)
    
    @classmethod
    async def _create_openai_provider(cls, settings: JarvisSettings) -> OpenAIProvider:
        """Crea y configura el proveedor OpenAI."""
        if not settings.openai_api_key:
            raise ValueError("Se requiere una clave API de OpenAI")
            
        config = OpenAIConfig(
            api_key=settings.openai_api_key,
            model=settings.openai_model
        )
        return OpenAIProvider(config)
    
    @classmethod
    async def create_hybrid(
        cls, 
        primary_provider: str = 'lm_studio',
        fallback_provider: str = 'openai',
        settings: Optional[JarvisSettings] = None
    ) -> LLMProvider:
        """Crea un proveedor híbrido con respaldo automático.
        
        Args:
            primary_provider: Proveedor principal a utilizar.
            fallback_provider: Proveedor de respaldo en caso de fallo.
            settings: Configuración de la aplicación.
            
        Returns:
            Instancia del proveedor principal si está disponible, 
            de lo contrario, instancia del proveedor de respaldo.
        """
        settings = settings or JarvisSettings()
        
        try:
            # Intentar con el proveedor principal primero
            provider = await cls.create(primary_provider, settings)
            await provider.health_check()
            return provider
        except Exception as e:
            logger.warning(f"No se pudo inicializar {primary_provider}: {e}")
            logger.info(f"Usando {fallback_provider} como respaldo")
            return await cls.create(fallback_provider, settings)