"""
Módulo de servicios para la API de SafeWaters.

Este módulo contiene la lógica de negocio para las operaciones de la API,
como la verificación de URLs contra múltiples fuentes de inteligencia de amenazas.
"""
from app.utils.cache import get_from_cache, set_to_cache
from app.utils.external_apis.abuseipdb import check_abuseipdb
from app.utils.external_apis.threatfox import check_threatfox
from app.utils.external_apis.urlscanio import check_urlscanio
from app.utils.domain_utils import get_ip_from_url, get_domain_from_url

async def check_url(url: str) -> dict:
    """Verifica si una URL es maliciosa consultando varias fuentes.

    Esta función sigue los siguientes pasos:
    1. Revisa la caché para obtener resultados previos para el dominio.
    2. Si no está en caché, consulta URLScan.io.
    3. Si URLScan.io no lo marca como malicioso, consulta ThreatFox.
    4. Si ThreatFox no lo marca como malicioso, obtiene la IP del dominio y consulta AbuseIPDB.
    5. Guarda el resultado final en caché.

    Args:
        url (str): La URL completa a verificar.

    Returns:
        dict: Un diccionario con la siguiente estructura:
            * ``domain`` (str): El dominio extraído de la URL.
            * ``malicious`` (bool): True si la URL se considera maliciosa, False en caso contrario.
            * ``info`` (str): Información adicional sobre el resultado.
            * ``source`` (str): La fuente que determinó el estado (Cache, URLScan.io, etc.).
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
    try:
        ip_address = await get_ip_from_url(domain)
    except Exception as e:
        # Si no se puede obtener la IP, se considera seguro
        set_to_cache(domain, False, "No se pudo obtener la IP del dominio.")
        return {
            "domain": domain,
            "malicious": False,
            "info": "No se pudo obtener la IP del dominio.",
            "source": "Multi-API"
        }

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


async def check_and_record_url(profile_token: str, url: str) -> dict:
    """
    Verifica una URL contra reglas de bloqueo y APIs de seguridad, y registra la navegación.
    
    Flujo unificado para la extensión del navegador que:
    1. Registra la navegación (siempre se ejecuta)
    2. Si fue bloqueada por regla de usuario, retorna información de bloqueo
    3. Si no está bloqueada, verifica contra APIs de seguridad
    4. Retorna resultado completo en formato URLResponse
    
    Args:
        profile_token (str): Token del perfil que realiza la navegación
        url (str): URL completa visitada
        
    Returns:
        dict: Diccionario compatible con URLResponse que incluye:
            - Información de verificación de seguridad
            - Estado de bloqueo por reglas de usuario
            (La navegación se registra internamente pero no se incluye en la respuesta)
    """
    try:
        from app.crud.crud_managed_profile import managed_profile_crud
        from app.crud.crud_navigation_history import navigation_history_crud
        
        # 1. Validar perfil
        profile = await managed_profile_crud.get_by_token(profile_token)
        if not profile:
            raise ValueError("Token de perfil no válido")
        
        # 2. Registrar navegación (siempre se ejecuta)
        navigation = await navigation_history_crud.create_from_profile_id_without_user_check(
            str(profile.id), 
            url
        )
        
        domain = get_domain_from_url(url)
        
        # 3. Si fue bloqueada por regla de usuario
        if navigation.blocked:
            blocking_details = "URL bloqueada por reglas del perfil"
            if navigation.blocking_rule_snapshot:
                blocking_details = f"Bloqueado por regla {navigation.blocking_rule_snapshot.rule_type}: {navigation.blocking_rule_snapshot.rule_value}"
            
            return {
                "domain": domain,
                "malicious": False,  # No se verificó contra APIs porque está bloqueada
                "info": "URL bloqueada por reglas de filtrado del perfil",
                "source": "User Rules",
                "is_blocked_by_user_rule": True,
                "blocking_rule_details": blocking_details
            }
        
        # 4. Si no está bloqueada, verificar contra APIs de seguridad
        security_result = await check_url(url)
        
        return {
            "domain": security_result["domain"],
            "malicious": security_result["malicious"],
            "info": security_result["info"],
            "source": security_result["source"],
            "is_blocked_by_user_rule": False,
            "blocking_rule_details": None
        }
        
    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise Exception(f"Error al verificar y registrar URL: {str(e)}")