import memcache
from app.config import settings 
import json
import logging

logger = logging.getLogger(__name__)

MEMCACHED_HOST = settings.MEMCACHED_HOST
MEMCACHED_PORT = settings.MEMCACHED_PORT
MEMCACHED_TIMEOUT = settings.MEMCACHED_TIMEOUT


client = memcache.Client([f"{MEMCACHED_HOST}:{MEMCACHED_PORT}"], debug=0)

def get_from_cache(domain: str) -> dict | None:
    """Intenta obtener los datos de Memcached y los deserializa."""
    try:
        cached_data = client.get(str(domain).encode("utf-8"))
        if cached_data:
            try:
                return json.loads(cached_data)
            except json.JSONDecodeError:
                logger.warning(f"Error al decodificar JSON de la caché para el dominio: {domain}")
                return None
        return None
    except Exception as e:
        logger.error(f"Error al acceder a Memcached (get) para el dominio {domain}: {str(e)}")
        return None

def set_to_cache(domain: str, malicious: bool, info: str):
    """Guarda solo la información relevante en Memcached usando la URL como clave."""
    data = {
        "malicious": malicious,
        "info": info
    }
    try:
        cached_data = json.dumps(data)
        client.set(domain, cached_data, time=MEMCACHED_TIMEOUT)
    except Exception as e:
        logger.error(f"Error al acceder a Memcached (set) para el dominio {domain}: {str(e)}")