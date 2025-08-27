# -*- coding: utf-8 -*-
"""
utils/logger.py — Sistema de logging con nivel por config y formato configurable.
"""
import logging
import structlog
import sys
from pathlib import Path
from typing import Optional

from ..config import JarvisSettings


def setup_logging(settings: JarvisSettings):
    """Configura el sistema de logging.
    
    Args:
        settings: Configuración de la aplicación. Si es None, se usa el módulo settings importado.
    """
    # Usar configuración global si no se proporciona settings
    
    
    # Crear directorio de logs si no existe
    if settings.log_file:
        log_path = Path(settings.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configurar nivel de log
    log_level = getattr(logging, settings.log_level.upper())
    log_format = settings.log_format
    
    # Configurar formateo
    if log_format == "json":
        structlog.configure(
            processors=[
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
        )
    else:
        structlog.configure(
            processors=[
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                structlog.dev.ConsoleRenderer(colors=True)
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
        )
    
    # Configurar handlers
    handlers = []
    
    # Handler de consola
    console_handler = logging.StreamHandler(sys.stdout)
    handlers.append(console_handler)
    
    # Handler de archivo si está configurado
    if settings.log_file:
        file_handler = logging.FileHandler(settings.log_file, encoding='utf-8')
        handlers.append(file_handler)
    
    # Configuración básica de logging
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        format='%(message)s'
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Obtiene un logger configurado.
    
    Args:
        name: Nombre del logger.
        
    Returns:
        Logger configurado.
    """
    return structlog.get_logger(name)
