import memcache
from app.config import settings 
import json

MEMCACHED_HOST = settings.MEMCACHED_HOST
MEMCACHED_PORT = settings.MEMCACHED_PORT
MEMCACHED_TIMEOUT = settings.MEMCACHED_TIMEOUT


client = memcache.Client([f"{MEMCACHED_HOST}:{MEMCACHED_PORT}"], debug=0)

def get_from_cache(url: str) -> dict | None:
    """Intenta obtener los datos de Memcached y los deserializa."""
    cached_data = client.get(str(url).encode("utf-8"))
    if cached_data:
        try:
            return json.loads(cached_data)
        except json.JSONDecodeError:
            return None
    return None

def set_to_cache(url: str, malicious: bool, info: str):
    """Guarda solo la información relevante en Memcached usando la URL como clave."""
    data = {
        "malicious": malicious,
        "info": info
    }
    # Serializar los datos como JSON y guardarlos en Memcached
    cached_data = json.dumps(data)
    client.set(url, cached_data, time=MEMCACHED_TIMEOUT)
