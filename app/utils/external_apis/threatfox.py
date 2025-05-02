from app.config import settings
import httpx

from app.models.urls import URLResponse
from app.models.url_threatfox import ThreatFoxResponse

THREATFOX_API_KEY = settings.THREATFOX_API_KEY
THREATFOX_API_URL = settings.THREATFOX_API_URL

async def check_threatfox(domain: str) -> URLResponse:
    """
    Consulta ThreatFox de forma asincrónica con un Dominio y devuelve los datos relevantes si se encuentra información.
    """
    payload = {
        "query": "search_ioc",
        "search_term": domain,
        "exact_match": True
    }

    headers = {
        "Auth-Key": THREATFOX_API_KEY
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:

            response = await client.post(THREATFOX_API_URL, params=payload, headers=headers)
            response.raise_for_status()
            parsed = ThreatFoxResponse.parse_raw(response.text)
            data = parsed.data

            if parsed.query_status == "ok":
                ioc_confiable = max((
                    ioc for ioc in data if ioc.confidence_level >= 50),
                    key=lambda ioc: ioc.confidence_level, default=None
                )
                if ioc_confiable:
                    return URLResponse(
                        domain=domain,
                        malicious=True,
                        info=f"IOC {ioc_confiable.ioc} reportado. "
                            f"Score: {ioc_confiable.confidence_level}. Uso: {ioc_confiable.threat_type or 'Desconocido'}. "
                            f"Fuente: ThreatFox",
                        source="ThreatFox"
                    )
                else:
                    return URLResponse(
                        domain=domain,
                        malicious=False,
                        info="Error: consulta exitosa, pero sin IOCs confiables (>= 50) para este dominio.",
                        source="ThreatFox"
                    )
            else:
                return URLResponse(
                    domain=domain,
                    malicious=False,
                    info="Error en la consulta a ThreatFox. Dominio no registrado.",
                    source="ThreatFox"
                )

    except httpx.RequestError as e:
        return URLResponse(
            domain=domain,
            malicious=False,
            info=f"Error de conexión: {str(e)}",
            source="ThreatFox"
        )

    except httpx.HTTPStatusError as e:
        return URLResponse(
            domain=domain,
            malicious=False,
            info=f"Error HTTP {e.response.status_code}: {e.response.text}",
            source="ThreatFox"
        )

    except Exception as e:
        return URLResponse(
            domain=domain,
            malicious=False,
            info=f"Error inesperado: {str(e)}",
            source="ThreatFox"
        )
