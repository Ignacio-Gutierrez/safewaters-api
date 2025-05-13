from urllib.parse import urlparse
import socket
import asyncio

def get_domain_from_url(url: str) -> str:
    """
    Extrae el dominio (hostname) de una URL.
    """
    return urlparse(url).hostname


async def get_ip_from_url(domain: str) -> str:
    """
    Dada una Dominio, devuelve su dirección IP de forma asíncrona.
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