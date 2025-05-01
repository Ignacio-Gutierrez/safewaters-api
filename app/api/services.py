from app.utils.cache import get_from_cache, set_to_cache
from app.utils.external_apis.abuseipdb import check_abuseipdb
from app.utils.utils import get_ip_from_url

async def check_url(url: str) -> dict:
    """
    Verifica si una URL es maliciosa consultando el caché, AbuseIPDB y ThreatFox.
    Devuelve un diccionario con información estandarizada sobre la peligrosidad.
    """
    # 1. Revisar el caché
    cached_result = get_from_cache(url)
    if cached_result:
        return {
            "url": url,
            "malicious": cached_result["malicious"],
            "info": cached_result["info"],
            "source": "Cache"
        }
    
    else:
        # 2. Consultar AbuseIPDB
        ip_address = await get_ip_from_url(url)
        abuseipdb_result = await check_abuseipdb(url, ip_address)

        # 3. Guardar en caché si hay información relevante
        if abuseipdb_result.info and "reportada" in abuseipdb_result.info:
            set_to_cache(url, abuseipdb_result.malicious, abuseipdb_result.info)
  
        # 4. Devolver el resultado
        return {
            "url": url,
            "malicious": abuseipdb_result.malicious,
            "info": abuseipdb_result.info,
            "source": "AbuseIPDB"
        }