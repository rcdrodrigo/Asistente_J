# -*- coding: utf-8 -*-
"""
scaffold_jarvis.py
Crea la arquitectura de carpetas/archivos para el proyecto 'jarvis'.
Uso:
  python scaffold_jarvis.py               # crea ./jarvis
  python scaffold_jarvis.py --path RUTA   # crea RUTA/jarvis
  python scaffold_jarvis.py --force       # sobrescribe archivos existentes
"""
from __future__ import annotations
import argparse
import os
from pathlib import Path
from textwrap import dedent

# ---------- Plantillas de archivos ----------
HEADER = "# -*- coding: utf-8 -*-\n"

def license_and_doc(title: str, summary: str = "") -> str:
    return dedent(f'''\
    {HEADER}"""
    {title}
    {summary}
    """
    ''')

MAIN_PY = dedent(f'''\
{HEADER}"""
main.py — Punto de entrada del asistente.
"""
from utils.logger import get_logger
from core.session import Session
from core.agent import Agent
from providers.factory import ProviderFactory
from config import settings

log = get_logger(__name__)

def run():
    log.info("Iniciando Jarvis…")
    session = Session()
    provider = ProviderFactory.from_settings(settings)
    agent = Agent(provider=provider, session=session)
    print("Jarvis listo. Escribe 'salir' para terminar.")
    while True:
        try:
            user = input("Tú: ").strip()
            if user.lower() in {{'salir', 'exit', 'quit'}}:
                break
            resp = agent.respond(user)
            print("Jarvis:", resp)
        except KeyboardInterrupt:
            break
        except Exception as e:
            log.exception("Error en loop principal: %s", e)
    log.info("Hasta luego.")

if __name__ == "__main__":
    run()
''')

CONFIG_PY = dedent(f'''\
{HEADER}"""
config.py — Configuración de la app (simple).
Sustituye por tu gestor preferido (.env, pydantic, dynaconf, etc.).
"""
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    PROVIDER: str = os.getenv("JARVIS_PROVIDER", "openai")  # 'openai' | 'ollama'
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    LOG_LEVEL: str = os.getenv("JARVIS_LOG_LEVEL", "INFO")

settings = Settings()
''')

EXCEPTIONS_PY = dedent(f'''\
{HEADER}"""
exceptions.py — Excepciones personalizadas.
"""
class JarvisError(Exception):
    """Error genérico de Jarvis."""

class ProviderNotConfigured(JarvisError):
    """Proveedor no configurado correctamente."""
''')

# --- core ---
CORE_AGENT = dedent(f'''\
{HEADER}"""
core/agent.py — Orquesta el flujo entre usuario, proveedor y herramientas.
"""
from typing import Optional
from utils.logger import get_logger
from tools.registry import ToolRegistry

log = get_logger(__name__)

class Agent:
    def __init__(self, provider, session):
        self.provider = provider
        self.session = session
        self.tools = ToolRegistry.default_registry()

    def respond(self, prompt: str) -> str:
        # Routing simple: si comienza con "!tool", intenta invocar herramienta.
        if prompt.startswith("!"):
            return self._handle_tool_command(prompt[1:].strip())
        history = self.session.as_messages() + [{{"role":"user","content":prompt}}]
        reply = self.provider.chat(history)
        self.session.add("user", prompt)
        self.session.add("assistant", reply)
        return reply

    def _handle_tool_command(self, cmd: str) -> str:
        # Formato: !nombre_tool arg1 arg2 ...
        parts = cmd.split()
        if not parts:
            return "Comando de herramienta vacío."
        name, *args = parts
        tool = self.tools.get(name)
        if not tool:
            return f"Herramienta '{{name}}' no encontrada. Usa !help para ver opciones."
        try:
            return tool.run(*args)
        except TypeError:
            return tool.help()
        except Exception as e:
            log.exception("Error al ejecutar herramienta %s", name)
            return f"Error en herramienta '{{name}}': {{e}}"
''')

CORE_SESSION = dedent(f'''\
{HEADER}"""
core/session.py — Maneja el historial de conversación.
"""
from typing import List, Dict

class Session:
    def __init__(self):
        self.messages: List[Dict[str,str]] = []

    def add(self, role: str, content: str):
        self.messages.append({{"role": role, "content": content}})

    def as_messages(self) -> List[Dict[str,str]]:
        return list(self.messages)
''')

# --- providers ---
PROVIDERS_INIT = HEADER
PROVIDERS_BASE = dedent(f'''\
{HEADER}"""
providers/base.py — Interfaz base para proveedores LLM.
"""
from abc import ABC, abstractmethod
from typing import List, Dict

class BaseProvider(ABC):
    @abstractmethod
    def chat(self, messages: List[Dict[str,str]]) -> str:
        ...
''')

PROVIDERS_FACTORY = dedent(f'''\
{HEADER}"""
providers/factory.py — Selecciona proveedor según config.
"""
from .base import BaseProvider
from .openai import OpenAIProvider
from .ollama import OllamaProvider
from config import settings
from exceptions import ProviderNotConfigured

class ProviderFactory:
    @staticmethod
    def from_settings(cfg=settings) -> BaseProvider:
        if cfg.PROVIDER.lower() == "openai":
            if not cfg.OPENAI_API_KEY:
                raise ProviderNotConfigured("Falta OPENAI_API_KEY.")
            return OpenAIProvider(model=cfg.OPENAI_MODEL, api_key=cfg.OPENAI_API_KEY)
        elif cfg.PROVIDER.lower() == "ollama":
            return OllamaProvider(model=cfg.OLLAMA_MODEL, base_url=cfg.OLLAMA_BASE_URL)
        else:
            raise ProviderNotConfigured(f"Proveedor no soportado: {{cfg.PROVIDER}}")
''')

PROVIDERS_OPENAI = dedent(f'''\
{HEADER}"""
providers/openai.py — Cliente mínimo para OpenAI-compatible.
"""
from typing import List, Dict
import os
import json
import urllib.request
from .base import BaseProvider

class OpenAIProvider(BaseProvider):
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    def chat(self, messages: List[Dict[str,str]]) -> str:
        url = f"{{self.base_url}}/chat/completions"
        payload = {{"model": self.model, "messages": messages, "temperature": 0.2}}
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                     headers={{"Content-Type": "application/json",
                                              "Authorization": f"Bearer {{self.api_key}}"}})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode("utf-8"))
        return data.get("choices", [{{"message": {{"content": ""}}}}])[0]["message"]["content"].strip()
''')

PROVIDERS_OLLAMA = dedent(f'''\
{HEADER}"""
providers/ollama.py — Cliente simple para Ollama local.
"""
from typing import List, Dict
import json
import urllib.request
from .base import BaseProvider

class OllamaProvider(BaseProvider):
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def chat(self, messages: List[Dict[str,str]]) -> str:
        url = f"{{self.base_url}}/v1/chat/completions"
        payload = {{"model": self.model, "messages": messages, "temperature": 0.2}}
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                     headers={{"Content-Type": "application/json"}})
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read().decode("utf-8"))
        return data.get("choices", [{{"message": {{"content": ""}}}}])[0]["message"]["content"].strip()
''')

# --- tools ---
TOOLS_BASE = dedent(f'''\
{HEADER}"""
tools/base.py — Clase base para herramientas.
"""
from abc import ABC, abstractmethod

class BaseTool(ABC):
    name: str = "tool"
    description: str = "Herramienta genérica"

    @abstractmethod
    def run(self, *args, **kwargs) -> str:
        ...

    def help(self) -> str:
        return f"{{self.name}}: {{self.description}}"
''')

TOOLS_REGISTRY = dedent(f'''\
{HEADER}"""
tools/registry.py — Registro de herramientas disponibles.
"""
from typing import Dict
from .base import BaseTool
from .system_info import SystemInfoTool
from .documentation import DocTool
from .git_operations import GitTool
from .file_analysis import FileAnalysisTool
from .code_execution import CodeRunTool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {{}}

    def add(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get(self, name: str):
        return self._tools.get(name)

    @classmethod
    def default_registry(cls):
        reg = cls()
        reg.add(SystemInfoTool())
        reg.add(DocTool())
        reg.add(GitTool())
        reg.add(FileAnalysisTool())
        reg.add(CodeRunTool())
        return reg
''')

TOOLS_CODE_EXEC = dedent(f'''\
{HEADER}"""
tools/code_execution.py — Ejecuta código Python en un entorno controlado (muy básico).
"""
import runpy
import tempfile
from .base import BaseTool

class CodeRunTool(BaseTool):
    name = "runpy"
    description = "Ejecuta un script Python aislado: !runpy print(\'hola\')"

    def run(self, *code: str) -> str:
        src = " ".join(code)
        with tempfile.TemporaryDirectory() as td:
            path = f"{{td}}/snippet.py"
            with open(path, "w", encoding="utf-8") as f:
                f.write(src)
            try:
                runpy.run_path(path, run_name="__main__")
                return "Ejecución OK (sin salida capturada)."
            except SystemExit as e:
                return f"Finalizó con SystemExit: {{e.code}}"
            except Exception as e:
                return f"Error al ejecutar: {{e}}"
''')

TOOLS_FILE_ANALYSIS = dedent(f'''\
{HEADER}"""
tools/file_analysis.py — Lee y resume archivos de texto (simple).
"""
from .base import BaseTool
from pathlib import Path

class FileAnalysisTool(BaseTool):
    name = "file"
    description = "Lee un archivo de texto: !file ruta/al/archivo.txt"

    def run(self, *args) -> str:
        if not args:
            return self.help()
        p = Path(args[0])
        if not p.exists():
            return f"Archivo no encontrado: {{p}}"
        text = p.read_text(encoding="utf-8", errors="ignore")
        snippet = text.strip().splitlines()[:20]
        return "\n".join(snippet) if snippet else "(archivo vacío)"
''')

TOOLS_GIT = dedent(f'''\
{HEADER}"""
tools/git_operations.py — Comandos mínimos de git vía CLI.
"""
import subprocess
from .base import BaseTool

class GitTool(BaseTool):
    name = "git"
    description = "Ejecuta comandos git: !git status | !git log -1"

    def run(self, *args) -> str:
        if not args:
            return self.help()
        try:
            out = subprocess.check_output(["git", *args], stderr=subprocess.STDOUT)
            return out.decode("utf-8", errors="ignore")
        except subprocess.CalledProcessError as e:
            return e.output.decode("utf-8", errors="ignore")
        except FileNotFoundError:
            return "git no está instalado o no está en PATH."
''')

TOOLS_SYSINFO = dedent(f'''\
{HEADER}"""
tools/system_info.py — Información básica del sistema.
"""
import platform
import shutil
from .base import BaseTool

class SystemInfoTool(BaseTool):
    name = "sys"
    description = "Muestra info del sistema: !sys"

    def run(self, *args) -> str:
        py = platform.python_version()
        osn = platform.system()
        arch = platform.machine()
        git = shutil.which("git") or "(no encontrado)"
        return f"Python: {{py}} | OS: {{osn}} | Arch: {{arch}} | git: {{git}}"
''')

TOOLS_DOC = dedent(f'''\
{HEADER}"""
tools/documentation.py — Devuelve ayuda corta.
"""
from .base import BaseTool

class DocTool(BaseTool):
    name = "help"
    description = "Lista de herramientas y uso."

    def run(self, *args) -> str:
        return (
            "Comandos:\n"
            "!help — esta ayuda\n"
            "!sys — info del sistema\n"
            "!git <cmd> — ejecuta git\n"
            "!file <ruta> — muestra primeras líneas de un archivo\n"
            "!runpy <código Python> — ejecuta un snippet\n"
        )
''')

# --- security ---
SEC_SANDBOX = dedent(f'''\
{HEADER}"""
security/sandbox.py — Lugar para aislar ejecuciones (placeholder).
"""
def is_allowed_path(path: str) -> bool:
    # Implementa tus reglas de acceso.
    return True
''')

SEC_VALIDATOR = dedent(f'''\
{HEADER}"""
security/validator.py — Validaciones básicas de entrada (placeholder).
"""
def validate_prompt(text: str) -> bool:
    return isinstance(text, str) and len(text) <= 8000
''')

SEC_PERMS = dedent(f'''\
{HEADER}"""
security/permissions.py — Permisos de funcionalidades (placeholder).
"""
def can_use_tool(user_role: str, tool_name: str) -> bool:
    return True
''')

SEC_AUDIT = dedent(f'''\
{HEADER}"""
security/audit.py — Registro de acciones sensibles (placeholder).
"""
def audit(event: str, **meta):
    # Envía a un log/sumidero seguro.
    pass
''')

# --- monitoring ---
MON_METRICS = dedent(f'''\
{HEADER}"""
monitoring/metrics.py — Métricas sencillas en memoria.
"""
from collections import defaultdict
_counts = defaultdict(int)

def inc(name: str):
    _counts[name] += 1

def dump() -> dict:
    return dict(_counts)
''')

MON_HEALTH = dedent(f'''\
{HEADER}"""
monitoring/health.py — Comprobación de salud (placeholder).
"""
def healthy() -> bool:
    return True
''')

MON_ALERTS = dedent(f'''\
{HEADER}"""
monitoring/alerts.py — Integración de alertas (placeholder).
"""
def notify(message: str):
    # Integra con email/Slack/Webhook
    pass
''')

# --- utils ---
UTILS_LOGGER = dedent(f'''\
{HEADER}"""
utils/logger.py — Logger básico con nivel por config.
"""
import logging
from config import settings

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(level)
        ch = logging.StreamHandler()
        fmt = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
        ch.setFormatter(fmt)
        logger.addHandler(ch)
    return logger
''')

UTILS_CACHE = dedent(f'''\
{HEADER}"""
utils/cache.py — Cache simple en memoria.
"""
from functools import lru_cache

@lru_cache(maxsize=256)
def memo(key: str) -> str:
    # Placeholder: almacena la propia clave.
    return key
''')

UTILS_HELPERS = dedent(f'''\
{HEADER}"""
utils/helpers.py — Utilidades varias (placeholder).
"""
def trim(s: str) -> str:
    return s.strip()
''')

def build_structure(base: Path) -> dict[str, str]:
    """Mapa path_relativo -> contenido."""
    return {
        # raíz
        "__init__.py": "",
        "main.py": MAIN_PY,
        "config.py": CONFIG_PY,
        "exceptions.py": EXCEPTIONS_PY,
        # core
        "core/__init__.py": "",
        "core/agent.py": CORE_AGENT,
        "core/session.py": CORE_SESSION,
        # providers
        "providers/__init__.py": PROVIDERS_INIT,
        "providers/base.py": PROVIDERS_BASE,
        "providers/factory.py": PROVIDERS_FACTORY,
        "providers/openai.py": PROVIDERS_OPENAI,
        "providers/ollama.py": PROVIDERS_OLLAMA,
        # tools
        "tools/__init__.py": "",
        "tools/base.py": TOOLS_BASE,
        "tools/registry.py": TOOLS_REGISTRY,
        "tools/code_execution.py": TOOLS_CODE_EXEC,
        "tools/file_analysis.py": TOOLS_FILE_ANALYSIS,
        "tools/git_operations.py": TOOLS_GIT,
        "tools/system_info.py": TOOLS_SYSINFO,
        "tools/documentation.py": TOOLS_DOC,
        # security
        "security/__init__.py": "",
        "security/sandbox.py": SEC_SANDBOX,
        "security/validator.py": SEC_VALIDATOR,
        "security/permissions.py": SEC_PERMS,
        "security/audit.py": SEC_AUDIT,
        # monitoring
        "monitoring/__init__.py": "",
        "monitoring/metrics.py": MON_METRICS,
        "monitoring/health.py": MON_HEALTH,
        "monitoring/alerts.py": MON_ALERTS,
        # utils
        "utils/__init__.py": "",
        "utils/logger.py": UTILS_LOGGER,
        "utils/cache.py": UTILS_CACHE,
        "utils/helpers.py": UTILS_HELPERS,
    }

def create_scaffold(root: Path, force: bool = False):
    """Crea la estructura de directorios y archivos."""
    structure = build_structure(root)
    print(f"Creando esqueleto en: {root.resolve()}")
    root.mkdir(exist_ok=True)

    for rel_path, content in structure.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists() and not force:
            print(f"  [Existe] {rel_path}")
            continue

        path.write_text(content, encoding="utf-8")
        print(f"  [Creado] {rel_path}")

def main():
    """Punto de entrada del script."""
    parser = argparse.ArgumentParser(description="Crea la estructura para el proyecto Jarvis.")
    parser.add_argument("--path", type=str, default=".", help="Ruta base donde crear la carpeta 'jarvis'")
    parser.add_argument("--force", action="store_true", help="Sobrescribir archivos existentes.")
    args = parser.parse_args()

    project_path = Path(args.path) / "jarvis"
    create_scaffold(project_path, args.force)
    print("\n¡Listo! Estructura creada.")

if __name__ == "__main__":
    main()
