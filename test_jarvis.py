"""
Script de prueba para JARVIS en Windows.

Este script verifica la configuración y funcionalidad básica de JARVIS en Windows.
"""

import asyncio
import os
import sys
import logging
import aiohttp
from pathlib import Path

# Configurar logging básico para ver mensajes de depuración
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Añadir el directorio raíz al path para poder importar los módulos
sys.path.insert(0, str(Path(__file__).parent.absolute()))

try:
    from jarvis.providers.ollama import OllamaProvider
    from jarvis.utils.logger import get_logger
    
    # Configurar logger
    logger = get_logger("test_jarvis")
except Exception as e:
    logger = logging.getLogger("test_jarvis")
    logger.error(f"Error al importar módulos de JARVIS: {e}")
    raise

async def test_ollama_connection():
    """Prueba la conexión con Ollama."""
    logger.info(" Iniciando prueba de conexión con Ollama...")
    
    # Configuración para Windows
    provider = OllamaProvider(
        model="deepseek-coder:6.7b",
        base_url="http://localhost:11434"
    )
    
    try:
        logger.info(" Inicializando proveedor Ollama...")
        await provider.initialize()

        # Verificar disponibilidad
        if not provider.is_available:
            logger.error(" Ollama no está disponible. Asegúrate de que el servidor esté en ejecución.")
            logger.info(" Intenta ejecutar: ollama serve")
            return False
        logger.info(" Proveedor Ollama inicializado correctamente")
        
        # Probar generación de texto
        prompt = "Escribe una función en Python que sume dos números"
        logger.info(f" Enviando prompt: {prompt}")
        
        logger.info(" Esperando respuesta de Ollama (esto puede tomar un momento)...")
        response = await provider.generate(prompt, max_tokens=200)
        
        if not response:
            logger.error(" No se recibió respuesta de Ollama")
            return False
            
        logger.info(" Respuesta recibida exitosamente")
        logger.info(" Respuesta:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        
        return True
        
    except asyncio.TimeoutError:
        logger.error(" Tiempo de espera agotado. El servidor Ollama podría estar sobrecargado.")
        return False
    except ConnectionError as e:
        logger.error(f" Error de conexión con Ollama: {e}")
        logger.info(" Verifica que el servidor Ollama esté en ejecución y accesible en http://localhost:11434")
        return False
    except Exception as e:
        logger.error(f" Error inesperado: {e}", exc_info=True)
        return False
    finally:
        try:
            await provider.cleanup()
        except Exception as e:
            logger.warning(f"Advertencia al limpiar el proveedor: {e}")

async def main():
    """Función principal de prueba."""
    print("\n" + "="*80)
    print(" PRUEBA DE JARVIS EN WINDOWS")
    print("="*80)
    
    # Verificar que Ollama está en ejecución
    try:
        logger.info(" Verificando conexión con Ollama...")
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/version", timeout=5) as resp:
                if resp.status != 200:
                    logger.error(" No se pudo conectar con Ollama")
                    logger.info(" Asegúrate de que el servidor Ollama esté en ejecución:")
                    logger.info("1. Abre una nueva terminal")
                    logger.info("2. Ejecuta: ollama serve")
                    logger.info("3. Mantén esa terminal abierta")
                    return False
                
                data = await resp.json()
                logger.info(f" Conectado a Ollama v{data.get('version', 'desconocida')}")
                
    except asyncio.TimeoutError:
        logger.error(" Tiempo de espera agotado al conectar con Ollama")
        logger.info(" El servidor Ollama podría no estar respondiendo o estar sobrecargado")
        return False
        
    except Exception as e:
        logger.error(f" Error al conectar con Ollama: {e}")
        logger.info(" Asegúrate de que el servidor Ollama esté en ejecución:")
        logger.info("1. Abre una nueva terminal")
        logger.info("2. Ejecuta: ollama serve")
        logger.info("3. Mantén esa terminal abierta")
        return False
    
    # Ejecutar pruebas
    logger.info("\n Iniciando pruebas de JARVIS...")
    
    # Prueba de conexión con Ollama
    logger.info("\n Probando conexión con el proveedor Ollama...")
    success = await test_ollama_connection()
    
    if success:
        logger.info("\n Todas las pruebas se completaron exitosamente")
        logger.info(" JARVIS está listo para ser usado")
    else:
        logger.error("\n Algunas pruebas fallaron. Revisa los mensajes de error para más detalles.")
        logger.info(" Si necesitas ayuda, verifica que:")
        logger.info(" - El servidor Ollama esté en ejecución")
        logger.info(" - El modelo 'deepseek-coder:6.7b' esté descargado")
        logger.info(" - No haya errores de red o permisos")
    
    return success

if __name__ == "__main__":
    # Configurar el bucle de eventos para Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        # Ejecutar pruebas
        exit_code = 0 if asyncio.run(main()) else 1
    except KeyboardInterrupt:
        logger.info("\n🛑 Pruebas canceladas por el usuario")
        exit_code = 1
    except Exception as e:
        logger.error(f"\n❌ Error inesperado: {e}", exc_info=True)
        exit_code = 1
    
    # Terminar con el código de salida apropiado
    sys.exit(exit_code)
