# -*- coding: utf-8 -*-
"""
Sistema de manejo de excepciones para JARVIS.

Este módulo define una jerarquía de excepciones personalizadas para manejar
los diferentes tipos de errores que pueden ocurrir en la aplicación.
"""
from typing import Optional, Dict, Any, Type, TypeVar, Union
from enum import Enum
import logging
import traceback

# Configure logger
logger = logging.getLogger(__name__)

# Type variable for error handling
T = TypeVar('T', bound='JarvisError')

class ErrorSeverity(Enum):
    """Niveles de severidad para los errores."""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

class JarvisError(Exception):
    """
    Clase base para todas las excepciones personalizadas de JARVIS.
    
    Args:
        message: Descripción del error.
        code: Código de error único.
        severity: Nivel de severidad del error.
        details: Información adicional sobre el error.
        cause: Excepción que causó este error (para chaining).
    """
    
    def __init__(
        self,
        message: str = "Ocurrió un error en JARVIS",
        code: str = "JARVIS_ERROR",
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        self.message = message
        self.code = code
        self.severity = severity
        self.details = details or {}
        self.cause = cause
        
        # Loguear el error según su severidad
        self._log_error()
        
        super().__init__(self.message)
    
    def _log_error(self) -> None:
        """Registra el error en el logger con el nivel de severidad apropiado."""
        log_message = f"[{self.code}] {self.message}"
        
        if self.severity == ErrorSeverity.DEBUG:
            logger.debug(log_message, exc_info=True, extra=self.details)
        elif self.severity == ErrorSeverity.INFO:
            logger.info(log_message, extra=self.details)
        elif self.severity == ErrorSeverity.WARNING:
            logger.warning(log_message, extra=self.details)
        elif self.severity == ErrorSeverity.ERROR:
            logger.error(log_message, exc_info=True, extra=self.details)
        else:  # CRITICAL
            logger.critical(log_message, exc_info=True, extra=self.details)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la excepción a un diccionario para serialización."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "severity": self.severity.name,
                "details": self.details,
                "cause": str(self.cause) if self.cause else None,
                "type": self.__class__.__name__
            }
        }
    
    @classmethod
    def from_exception(
        cls: Type[T],
        exc: Exception,
        message: Optional[str] = None,
        code: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        **details: Any
    ) -> T:
        """Crea una excepción JarvisError a partir de otra excepción."""
        return cls(
            message=message or str(exc) or "Ocurrió un error inesperado",
            code=code or "UNEXPECTED_ERROR",
            severity=severity,
            details={"original_exception": exc.__class__.__name__, **details},
            cause=exc
        )


# ===== Errores de Configuración =====
class ConfigurationError(JarvisError):
    """Error en la configuración de la aplicación."""
    def __init__(self, message: str, **details: Any):
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            severity=ErrorSeverity.ERROR,
            details=details
        )

class ProviderNotConfigured(ConfigurationError):
    """Proveedor no configurado correctamente."""
    def __init__(self, provider_name: str, **details: Any):
        super().__init__(
            message=f"El proveedor '{provider_name}' no está configurado correctamente",
            code="PROVIDER_NOT_CONFIGURED",
            severity=ErrorSeverity.ERROR,
            details={"provider": provider_name, **details}
        )

# ===== Errores de Herramientas =====
class ToolError(JarvisError):
    """Error al ejecutar una herramienta."""
    def __init__(self, tool_name: str, message: str, **details: Any):
        super().__init__(
            message=f"Error en la herramienta '{tool_name}': {message}",
            code="TOOL_ERROR",
            severity=ErrorSeverity.ERROR,
            details={"tool": tool_name, **details}
        )

class ToolExecutionError(ToolError):
    """Error durante la ejecución de una herramienta."""
    def __init__(self, tool_name: str, command: str, **details: Any):
        super().__init__(
            tool_name=tool_name,
            message=f"Error al ejecutar el comando: {command}",
            code="TOOL_EXECUTION_ERROR",
            details={"command": command, **details}
        )

# ===== Errores de Voz =====
class VoiceError(JarvisError):
    """Error relacionado con el procesamiento de voz."""
    def __init__(self, message: str, **details: Any):
        super().__init__(
            message=message,
            code="VOICE_ERROR",
            severity=ErrorSeverity.ERROR,
            details=details
        )

class SpeechRecognitionError(VoiceError):
    """Error en el reconocimiento de voz."""
    def __init__(self, **details: Any):
        super().__init__(
            message="Error al reconocer el habla",
            code="SPEECH_RECOGNITION_ERROR",
            details=details
        )

class SpeechSynthesisError(VoiceError):
    """Error en la síntesis de voz."""
    def __init__(self, text: str, **details: Any):
        super().__init__(
            message=f"Error al sintetizar el texto: {text[:50]}...",
            code="SPEECH_SYNTHESIS_ERROR",
            details={"text_preview": text[:200], **details}
        )

# ===== Errores de Seguridad =====
class SecurityError(JarvisError):
    """Error de seguridad."""
    def __init__(self, message: str, **details: Any):
        super().__init__(
            message=message,
            code="SECURITY_ERROR",
            severity=ErrorSeverity.CRITICAL,
            details=details
        )

class PermissionDeniedError(SecurityError):
    """Acceso denegado por permisos insuficientes."""
    def __init__(self, action: str, **details: Any):
        super().__init__(
            message=f"Permiso denegado para: {action}",
            code="PERMISSION_DENIED",
            details={"action": action, **details}
        )

def handle_error(
    func: callable = None,
    *,
    default_return: Any = None,
    raise_custom: Optional[Type[JarvisError]] = None,
    **error_kwargs
) -> Any:
    """
    Decorador para manejar errores de manera consistente.
    
    Args:
        func: Función a decorar.
        default_return: Valor a retornar en caso de error si no se relanza.
        raise_custom: Clase de excepción personalizada a lanzar.
        **error_kwargs: Argumentos adicionales para la excepción personalizada.
    
    Returns:
        Resultado de la función o valor por defecto en caso de error.
    """
    def decorator(f):
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except JarvisError:
                raise  # Ya manejado
            except Exception as e:
                if raise_custom:
                    raise raise_custom(**error_kwargs) from e
                if default_return is not None:
                    return default_return
                raise
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func)