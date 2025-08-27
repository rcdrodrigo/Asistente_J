import requests

ollama_url = "http://localhost:11434"

try:
    response = requests.get(f"{ollama_url}/api/version", timeout=5)
    response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
    print(f"Conexión exitosa a Ollama. Versión: {response.json()}")
except requests.exceptions.ConnectionError as e:
    print(f"Error de conexión: No se pudo conectar a Ollama en {ollama_url}. Asegúrate de que Ollama esté ejecutándose y no haya un firewall bloqueando la conexión.")
    print(f"Detalles del error: {e}")
except requests.exceptions.Timeout as e:
    print(f"Error de tiempo de espera: La conexión a Ollama en {ollama_url} excedió el tiempo límite.")
    print(f"Detalles del error: {e}")
except requests.exceptions.RequestException as e:
    print(f"Error inesperado al conectar con Ollama: {e}")