from app.utils.cache import get_from_cache, set_to_cache
from app.utils.external_apis.abuseipdb import check_abuseipdb
from app.utils.external_apis.threatfox import check_threatfox
from app.utils.external_apis.urlscanio import check_urlscanio
from app.utils.utils import get_ip_from_url, get_domain_from_url

async def check_url(url: str) -> dict:
    """
    Verifica si una URL es maliciosa consultando el caché, AbuseIPDB, URLScan.io y ThreatFox.
    Devuelve un diccionario con información estandarizada sobre la peligrosidad.
    """
    domain = get_domain_from_url(url)

    # 1. Revisar el caché
    cached_result = get_from_cache(domain)
    if cached_result:
        return {
            "domain": domain,
            "malicious": cached_result["malicious"],
            "info": cached_result["info"],
            "source": "Cache"
        }
    
    # 2. Consultar URLScan.io
    urlscanio_result = await check_urlscanio(domain)
    if urlscanio_result.malicious:
        set_to_cache(domain, urlscanio_result.malicious, urlscanio_result.info)
        return {
            "domain": domain,
            "malicious": urlscanio_result.malicious,
            "info": urlscanio_result.info,
            "source": urlscanio_result.source
        }
    
    # 3. Consultar ThreatFox
    threatfox_result = await check_threatfox(domain)
    if threatfox_result.malicious:
        set_to_cache(domain, threatfox_result.malicious, threatfox_result.info)
        return {
            "domain": domain,
            "malicious": threatfox_result.malicious,
            "info": threatfox_result.info,
            "source": threatfox_result.source
        }

    # 4. Consultar AbuseIPDB (requiere IP)
    ip_address = await get_ip_from_url(url)
    abuseipdb_result = await check_abuseipdb(domain, ip_address)
    if abuseipdb_result.malicious:
        set_to_cache(domain, abuseipdb_result.malicious, abuseipdb_result.info)
        return {
            "domain": domain,
            "malicious": abuseipdb_result.malicious,
            "info": abuseipdb_result.info,
            "source": abuseipdb_result.source
        }

    # 5. Si ninguna fuente lo detecta como malicioso, guardar resultado seguro en caché
    set_to_cache(domain, False, "No se detectaron señales de peligro en fuentes consultadas.")
    return {
        "domain": domain,
        "malicious": False,
        "info": "No se detectaron señales de peligro en fuentes consultadas.",
        "source": "Multi-API"
    }