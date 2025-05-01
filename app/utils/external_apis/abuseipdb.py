from app.config import settings
import httpx
from pydantic import BaseModel, HttpUrl

from app.models.urls import URLResponse
from app.models.url_abuseipdb import AbuseIPDBResponse

ABUSEIPDB_API_KEY = settings.ABUSEIPDB_API_KEY
ABUSEIPDB_API_URL = settings.ABUSEIPDB_API_URL

async def check_abuseipdb(domain: str, ip_address: str) -> URLResponse:
    """
    Consulta AbuseIPDB de forma asincrónica con una IP y devuelve un objeto URLResponse.
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
            info=f"Error de conexión: {str(e)}",
            source="AbuseIPDB"
        )

    except httpx.HTTPStatusError as e:
        return URLResponse(
            domain=domain,
            malicious=False,
            info=f"Error HTTP {e.response.status_code}: {e.response.text}",
            source="AbuseIPDB"
        )

    except Exception as e:
        return URLResponse(
            domain=domain,
            malicious=False,
            info=f"Error inesperado: {str(e)}",
            source="AbuseIPDB"
        )
