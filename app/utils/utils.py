from urllib.parse import urlparse
import socket

def get_domain_from_url(url: str) -> str:
    """
    Extrae el dominio (hostname) de una URL.
    """
    return urlparse(url).hostname


async def get_ip_from_url(domain: str) -> str:
    """
    Dada una Dominio, devuelve su dirección IP.
    """
    try:
        ip_address = socket.gethostbyname(domain)
        return ip_address
    except Exception as e:
        raise ValueError(f"No se pudo resolver la IP para el dominio {domain}: {str(e)}")
