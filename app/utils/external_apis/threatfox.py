"""
Módulo para interactuar con la API de ThreatFox de abuse.ch.

Este módulo proporciona funciones para consultar la API de ThreatFox y verificar
si un dominio está listado como un Indicador de Compromiso (IOC).
Utiliza la configuración de la aplicación para obtener la clave API y la URL base del servicio.
"""
from app.config import settings
import httpx

from app.models.urls import URLResponse
from app.models.url_threatfox import ThreatFoxResponse

THREATFOX_API_KEY = settings.THREATFOX_API_KEY
THREATFOX_API_URL = settings.THREATFOX_API_URL

async def check_threatfox(domain: str) -> URLResponse:
    """
    Consulta ThreatFox de forma asincrónica con un dominio y devuelve los datos relevantes.

    Realiza una solicitud POST a la API de ThreatFox para buscar IOCs asociados al dominio.
    Considera un dominio como malicioso si encuentra un IOC con un ``confidence_level >= 50``.
    Si hay múltiples IOCs confiables, se prioriza el de mayor ``confidence_level``.

    :param domain: El dominio a verificar.
    :type domain: str
    :return: Un objeto :class:`~app.models.urls.URLResponse` con el resultado de la verificación.
             Si la consulta es exitosa y se encuentra un IOC confiable, ``malicious`` será ``True``.
             Si no se encuentran IOCs confiables o el ``query_status`` no es "ok", ``malicious`` será ``False``.
             En caso de error (conexión, HTTP, u otro), ``malicious`` será ``False`` y ``info``
             contendrá el mensaje de error.
    :rtype: app.models.urls.URLResponse
    """
    payload = {
        "query": "search_ioc",
        "search_term": domain,
        "exact_match": True
    }

    headers = {
        "API-KEY": THREATFOX_API_KEY
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(THREATFOX_API_URL, params=payload, headers=headers)
            response.raise_for_status()
            parsed = ThreatFoxResponse.parse_raw(response.text)
            
            if parsed.query_status == "ok" and parsed.data:
                # Filtrar IOCs con confidence_level >= 50 y tomar el de mayor confianza
                ioc_confiable = max(
                    (ioc for ioc in parsed.data if ioc.confidence_level >= 50),
                    key=lambda ioc: ioc.confidence_level,
                    default=None
                )
                if ioc_confiable:
                    return URLResponse(
                        domain=domain,
                        malicious=True,
                        info=f"IOC '{ioc_confiable.ioc}' (Tipo: {ioc_confiable.threat_type}, Malware: {ioc_confiable.malware_printable}) reportado. "
                             f"Confianza: {ioc_confiable.confidence_level}. Fuente: ThreatFox",
                        source="ThreatFox"
                    )
                else:
                    return URLResponse(
                        domain=domain,
                        malicious=False,
                        info=f"Dominio '{domain}' no encontrado con IOCs confiables (confianza >= 50) en ThreatFox.",
                        source="ThreatFox"
                    )
            elif parsed.query_status == "no_result":
                 return URLResponse(
                    domain=domain,
                    malicious=False,
                    info=f"Dominio '{domain}' no encontrado en ThreatFox (no_result).",
                    source="ThreatFox"
                )
            else:
                return URLResponse(
                    domain=domain,
                    malicious=False,
                    info=f"Consulta a ThreatFox para '{domain}' devolvió estado: {parsed.query_status}.",
                    source="ThreatFox"
                )

    except httpx.RequestError as e:
        return URLResponse(
            domain=domain,
            malicious=False,
            info=f"Error de conexión con ThreatFox para '{domain}': {str(e)}",
            source="ThreatFox"
        )

    except httpx.HTTPStatusError as e:
        return URLResponse(
            domain=domain,
            malicious=False,
            info=f"Error HTTP {e.response.status_code} de ThreatFox para '{domain}': {e.response.text}",
            source="ThreatFox"
        )

    except Exception as e:
        return URLResponse(
            domain=domain,
            malicious=False,
            info=f"Error inesperado al procesar respuesta de ThreatFox para '{domain}': {str(e)}",
            source="ThreatFox"
        )