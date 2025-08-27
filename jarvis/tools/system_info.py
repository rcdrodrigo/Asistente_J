"""Herramienta de información del sistema para Windows."""
import psutil
import platform
from ..utils.logger import get_logger
from .base import BaseTool

logger = get_logger(__name__)

class SystemInfoTool(BaseTool):
    name: str = "system_info"
    description: str = "Proporciona información sobre el sistema operativo, CPU, memoria y disco."
    
    def __init__(self, settings):
        self.settings = settings
    
    async def run(self, info_type: str = "general") -> str:
        """Obtiene información del sistema."""
        try:
            if info_type == "general":
                return self._get_general_info()
            elif info_type == "cpu":
                return self._get_cpu_info()
            elif info_type == "memory":
                return self._get_memory_info()
            elif info_type == "disk":
                return self._get_disk_info()
            else:
                return self._get_general_info()
        except Exception as e:
            logger.error(f"Error obteniendo información del sistema: {e}")
            return f"❌ Error obteniendo información: {e}"
    
    def _get_general_info(self) -> str:
        """Información general del sistema."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('C:\\')
        
        return f"""💻 **Información del Sistema Windows**

🖥️ **Sistema Operativo:**
  • OS: {platform.system()} {platform.release()}
  • Versión: {platform.version()}
  • Arquitectura: {platform.machine()}

📊 **Recursos en Tiempo Real:**
  • CPU: {cpu_percent:.1f}% de uso
  • RAM: {memory.percent:.1f}% ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)
  • Disco C: {disk.percent:.1f}% ({disk.used // (1024**3):.1f}GB / {disk.total // (1024**3):.1f}GB)

🔋 **Estado:** {'🟢 Óptimo' if cpu_percent < 70 and memory.percent < 80 else '🟡 Uso elevado' if cpu_percent < 90 and memory.percent < 90 else '🔴 Uso crítico'}
"""
    
    def _get_cpu_info(self) -> str:
        """Información detallada de CPU."""
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        return f"""🔧 **Información de CPU**

💾 **Especificaciones:**
  • Núcleos lógicos: {cpu_count}
  • Frecuencia actual: {cpu_freq.current:.0f} MHz
  • Frecuencia máxima: {cpu_freq.max:.0f} MHz

📊 **Uso actual:**
  • CPU total: {cpu_percent:.1f}%
"""
    
    def _get_memory_info(self) -> str:
        """Información de memoria."""
        memory = psutil.virtual_memory()
        
        return f"""🧠 **Información de Memoria**

💾 **RAM:**
  • Total: {memory.total // (1024**3):.1f} GB
  • Usada: {memory.used // (1024**3):.1f} GB  
  • Disponible: {memory.available // (1024**3):.1f} GB
  • Porcentaje usado: {memory.percent:.1f}%
"""
    
    def _get_disk_info(self) -> str:
        """Información de discos."""
        disk_c = psutil.disk_usage('C:\\')
        
        return f"""💽 **Información de Discos**

📁 **Disco C:\\**
  • Total: {disk_c.total // (1024**3):.1f} GB
  • Usado: {disk_c.used // (1024**3):.1f} GB
  • Libre: {disk_c.free // (1024**3):.1f} GB
  • Porcentaje usado: {disk_c.percent:.1f}%
"""
