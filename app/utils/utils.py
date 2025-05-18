"""
Módulo de utilidades.

Este módulo proporciona funciones auxiliares generales, como la extracción
de dominios de URLs y la resolución de direcciones IP.
"""
from urllib.parse import urlparse
import socket
import asyncio

def get_domain_from_url(url: str) -> str:
    """
    Extrae el dominio (hostname) de una URL.

    :param url: La URL completa de la cual extraer el dominio.
    :type url: str
    :return: El nombre de host (dominio) extraído de la URL.
             Retorna ``None`` si la URL no tiene un hostname válido.
    :rtype: str
    """
    parsed_url = urlparse(url)
    return parsed_url.hostname


async def get_ip_from_url(domain: str) -> str:
    """
    Dada un dominio, devuelve su dirección IP de forma asíncrona.

    Intenta resolver la dirección IP del dominio especificado.
    Prioriza la primera dirección IP encontrada.

    :param domain: El nombre de dominio para el cual obtener la IP.
    :type domain: str
    :return: La dirección IP del dominio.
    :rtype: str
    :raises ValueError: Si ocurre un error durante la resolución de DNS
                        o si no se puede encontrar una dirección IP para el dominio.
    """
    try:
        loop = asyncio.get_running_loop()
        results = await loop.getaddrinfo(domain, None, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM)
        for res in results:
            ip_address = res[4][0]
            if ip_address:
                return ip_address
        raise ValueError(f"No se pudo encontrar una dirección IP en los resultados de getaddrinfo para el dominio {domain}")
    except socket.gaierror as e:
        raise ValueError(f"Error de resolución de DNS para el dominio {domain}: {str(e)}")
    except Exception as e:
        raise ValueError(f"No se pudo resolver la IP para el dominio {domain}: {str(e)}")