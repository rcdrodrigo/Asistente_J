"""
Script para configurar el entorno de desarrollo.
Copia .env.example a .env si no existe.
"""
from pathlib import Path
import shutil

def setup_env():
    env_example = Path(__file__).parent / ".env.example"
    env_file = Path(__file__).parent / ".env"
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print(f"Se ha creado el archivo {env_file} a partir de {env_example}")
    elif env_file.exists():
        print(f"El archivo {env_file} ya existe")
    else:
        print(f"Error: No se encontró el archivo {env_example}")

if __name__ == "__main__":
    setup_env()
