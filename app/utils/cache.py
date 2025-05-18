"""
Módulo de gestión de caché con Memcached.

Este módulo proporciona funciones para interactuar con un servidor Memcached,
permitiendo almacenar y recuperar resultados de verificaciones de URLs para
mejorar el rendimiento y reducir la carga en APIs externas.
"""
import memcache
from app.config import settings
import json
import logging

logger = logging.getLogger(__name__)
"""
Instancia del logger para este módulo.
"""

MEMCACHED_HOST = settings.MEMCACHED_HOST
"""
Host del servidor Memcached, obtenido de la configuración de la aplicación.

:type: str
"""
MEMCACHED_PORT = settings.MEMCACHED_PORT
"""
Puerto del servidor Memcached, obtenido de la configuración de la aplicación.

:type: int
"""
MEMCACHED_TIMEOUT = settings.MEMCACHED_TIMEOUT
"""
Tiempo de expiración para las entradas de caché en segundos, obtenido de la configuración.

:type: int
"""


client = memcache.Client([f"{MEMCACHED_HOST}:{MEMCACHED_PORT}"], debug=0)
"""
Cliente de Memcached.

Instancia de :class:`memcache.Client` configurada con el host y puerto especificados
en la configuración de la aplicación. El modo debug está desactivado (0).
"""

def get_from_cache(domain: str) -> dict | None:
    """
    Intenta obtener los datos de Memcached para un dominio y los deserializa.

    Busca en la caché una entrada asociada al dominio proporcionado. Si se encuentra,
    intenta decodificar los datos JSON almacenados.

    :param domain: El dominio a buscar en la caché.
    :type domain: str
    :return: Un diccionario con los datos cacheados (claves 'malicious' e 'info')
             si se encuentran y se decodifican correctamente.
             Retorna ``None`` si el dominio no está en caché, si ocurre un error
             al decodificar el JSON, o si hay un problema al conectar con Memcached.
    :rtype: dict | None
    """
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
    """
    Guarda información relevante en Memcached usando el dominio como clave.

    Serializa un diccionario conteniendo el estado de maliciosidad y la información
    adicional en formato JSON y lo almacena en Memcached.

    :param domain: El dominio que se usará como clave en la caché.
    :type domain: str
    :param malicious: Booleano indicando si el dominio es considerado malicioso.
    :type malicious: bool
    :param info: Información adicional sobre la detección.
    :type info: str
    :raises Exception: Registra un error si falla la conexión o la operación set en Memcached.
    """
    data = {
        "malicious": malicious,
        "info": info
    }
    try:
        cached_data = json.dumps(data)
        client.set(domain, cached_data, time=MEMCACHED_TIMEOUT)
    except Exception as e:
        logger.error(f"Error al acceder a Memcached (set) para el dominio {domain}: {str(e)}")