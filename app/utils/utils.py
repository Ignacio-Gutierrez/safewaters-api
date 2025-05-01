from urllib.parse import urlparse
import socket

async def get_ip_from_url(url: str) -> str:
    """
    Dada una URL, obtiene la IP asociada mediante resolución DNS.
    """
    try:
        hostname = urlparse(url).hostname
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except Exception as e:
        raise ValueError(f"No se pudo resolver la IP para la URL {url}: {str(e)}")
