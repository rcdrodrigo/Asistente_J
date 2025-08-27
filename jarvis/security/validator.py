"""
Módulo de validación de seguridad para JARVIS.

Proporciona validaciones de seguridad para la ejecución de código y otras operaciones.
"""

import ast
import re
import logging
from typing import List, Set, Optional
from pathlib import Path

from ..utils.logger import get_logger
from ..config import JarvisSettings

logger = get_logger(__name__)

class SecurityValidator:
    """Validador de seguridad para operaciones en JARVIS."""
    
    def __init__(self, settings):
        """Inicializa el validador con la configuración proporcionada."""
        self.settings = settings
        self._forbidden_imports = {
            'os', 'sys', 'subprocess', 'shutil', 'ctypes', 'win32api',
            'win32con', 'win32file', 'win32process', 'win32security',
            'socket', 'multiprocessing', 'threading', 'asyncio',
            'pickle', 'marshal', 'code', 'builtins', 'importlib',
            'imp', 'pipes', 'popen2', 'posix', 'pwd', 'resource',
            'spwd', 'syslog', 'tempfile', 'webbrowser'
        }
        
        self._forbidden_functions = {
            'eval', 'exec', 'execfile', 'compile', 'input',
            'open', 'file', 'exec', 'reload', '__import__',
            'exit', 'quit', 'help', 'license', 'copyright',
            'credits', 'input', 'raw_input', 'print'
        }
        
        self._forbidden_attributes = {
            '__dict__', '__globals__', '__code__',
            '__closure__', '__defaults__', '__kwdefaults__'
        }
        
        self._allowed_directories = set()
        if hasattr(settings, 'allowed_directories'):
            self._allowed_directories = set(settings.allowed_directories)
    
    def validate_code(self, code: str) -> None:
        """
        Valida que el código sea seguro para ejecutar.
        
        Args:
            code: Código a validar
            
        Raises:
            SecurityError: Si se detecta código potencialmente inseguro
        """
        try:
            # Validar patrones peligrosos
            self._check_dangerous_patterns(code)
            
            # Analizar AST para detectar operaciones inseguras
            self._analyze_ast(code)
            
        except SyntaxError as e:
            raise SecurityError(f"Error de sintaxis en el código: {e}")
        except Exception as e:
            raise SecurityError(f"Error validando código: {e}")
    
    def _check_dangerous_patterns(self, code: str) -> None:
        """Busca patrones potencialmente peligrosos en el código."""
        dangerous_patterns = [
            r'__[a-zA-Z0-9_]+__\s*\(',
            r'exec\s*\(',
            r'eval\s*\(',
            r'__import__\s*\('
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code):
                raise SecurityError(f"Se detectó un patrón potencialmente peligroso: {pattern}")
    
    def _analyze_ast(self, code: str) -> None:
        """Analiza el AST del código en busca de operaciones inseguras."""
        try:
            tree = ast.parse(code)
            
            class SecurityVisitor(ast.NodeVisitor):
                def __init__(self, validator):
                    self.validator = validator
                
                def visit_Import(self, node):
                    for name in node.names:
                        if name.name in self.validator._forbidden_imports:
                            raise SecurityError(f"Importación no permitida: {name.name}")
                    self.generic_visit(node)
                
                def visit_ImportFrom(self, node):
                    if node.module in self.validator._forbidden_imports:
                        raise SecurityError(f"Importación no permitida: {node.module}")
                    self.generic_visit(node)
                
                def visit_Call(self, node):
                    if isinstance(node.func, ast.Name) and node.func.id in self.validator._forbidden_functions:
                        raise SecurityError(f"Llamada a función no permitida: {node.func.id}")
                    self.generic_visit(node)
                
                def visit_Attribute(self, node):
                    if node.attr in self.validator._forbidden_attributes:
                        raise SecurityError(f"Acceso a atributo no permitido: {node.attr}")
                    self.generic_visit(node)
            
            visitor = SecurityVisitor(self)
            visitor.visit(tree)
            
        except Exception as e:
            raise SecurityError(f"Error analizando el AST: {e}")
    
    def validate_file_access(self, file_path: str, mode: str = 'r') -> None:
        """
        Valida si se permite el acceso a un archivo.
        
        Args:
            file_path: Ruta del archivo a validar
            mode: Modo de apertura del archivo
            
        Raises:
            SecurityError: Si el acceso al archivo no está permitido
        """
        try:
            path = Path(file_path).resolve()
            
            # Verificar si la ruta está dentro de un directorio permitido
            if self._allowed_directories:
                if not any(str(path).startswith(str(allowed)) for allowed in self._allowed_directories):
                    raise SecurityError(f"Acceso no permitido a la ruta: {file_path}")
            
            # Validar modo de apertura
            if 'w' in mode or 'a' in mode or '+' in mode:
                if not hasattr(self.settings, 'allow_file_writes') or not self.settings.allow_file_writes:
                    raise SecurityError("Escritura de archivos no permitida")
            
            # Validar extensión del archivo si es necesario
            if hasattr(self.settings, 'allowed_file_extensions'):
                if path.suffix.lower() not in self.settings.allowed_file_extensions:
                    raise SecurityError(f"Tipo de archivo no permitido: {path.suffix}")
                    
        except Exception as e:
            raise SecurityError(f"Error validando acceso a archivo: {e}")


class SecurityError(Exception):
    """Excepción lanzada cuando se detecta una violación de seguridad."""
    pass
