"""
Módulo para interactuar con la API de AbuseIPDB.

Este módulo proporciona funciones para consultar la API de AbuseIPDB y verificar
la reputación de una dirección IP. Utiliza la configuración de la aplicación
para obtener la clave API y la URL base del servicio.
"""
from app.config import settings
import httpx

from app.schemas.urls_check import URLResponse
from app.utils.external_api_models.abuseipdb_model import AbuseIPDBResponse

ABUSEIPDB_API_KEY = settings.ABUSEIPDB_API_KEY
ABUSEIPDB_API_URL = settings.ABUSEIPDB_API_URL

async def check_abuseipdb(domain: str, ip_address: str) -> URLResponse:
    """
    Consulta AbuseIPDB de forma asincrónica con una IP y devuelve un objeto URLResponse.

    Realiza una solicitud GET a la API de AbuseIPDB para obtener información sobre la IP
    proporcionada. Determina si la IP es maliciosa basándose en el ``abuseConfidenceScore``.

    :param domain: El dominio asociado a la IP (utilizado para la respuesta).
    :type domain: str
    :param ip_address: La dirección IP a verificar.
    :type ip_address: str
    :return: Un objeto :class:`~app.models.urls.URLResponse` con el resultado de la verificación.
             Si la consulta es exitosa, ``malicious`` será ``True`` si el ``abuseConfidenceScore >= 50``.
             En caso de error (conexión, HTTP, u otro), ``malicious`` será ``False`` y ``info``
             contendrá el mensaje de error.
    :rtype: app.models.urls.URLResponse
    """
    querystring = {
        'ipAddress': ip_address,
        'maxAgeInDays': '365'
    }

    headers = {
        'Accept': 'application/json',
        'Key': ABUSEIPDB_API_KEY
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(ABUSEIPDB_API_URL, headers=headers, params=querystring)
            response.raise_for_status()
            parsed = AbuseIPDBResponse.parse_raw(response.text)
            data = parsed.data

            return URLResponse(
                domain=domain,
                malicious=data.abuseConfidenceScore >= 50,
                info=f"IP {data.ipAddress} reportada {data.totalReports} vez/veces. "
                     f"Score: {data.abuseConfidenceScore}. Uso: {data.usageType or 'Desconocido'}. "
                     f"Fuente: AbuseIPDB",
                source="AbuseIPDB"
            )

    except httpx.RequestError as e:
        return URLResponse(
            domain=domain,
            malicious=False,
            info=f"Error de conexión con AbuseIPDB: {str(e)}",
            source="AbuseIPDB"
        )

    except httpx.HTTPStatusError as e:
        return URLResponse(
            domain=domain,
            malicious=False,
            info=f"Error HTTP {e.response.status_code} de AbuseIPDB: {e.response.text}",
            source="AbuseIPDB"
        )

    except Exception as e:
        return URLResponse(
            domain=domain,
            malicious=False,
            info=f"Error inesperado al procesar respuesta de AbuseIPDB: {str(e)}",
            source="AbuseIPDB"
        )