from app.config import settings
import httpx

from app.models.urls import URLResponse
from app.models.url_urlscanio import URLScanioResponse, ResultItem

URLSCANIO_API_KEY = settings.URLSCANIO_API_KEY
URLSCANIO_API_URL = settings.URLSCANIO_API_URL

def is_malicious(result: ResultItem) -> bool:
    tags = result.task.tags or []
    source = (result.task.source or "").lower()
    return any("phish" in tag.lower() for tag in tags) or "phish" in source or "suspicious" in source


async def check_urlscanio(domain: str) -> URLResponse:
    """
    Consulta URLScan.io de forma asincrónica con una URL y devuelve los datos relevantes si se encuentra información.
    """

    query = f"page.domain:{domain} AND date:>now-90d"

    headers = {
        "API-Key": URLSCANIO_API_KEY,
    }

    params = {
        "q": query, "size": 10
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(URLSCANIO_API_URL, headers=headers, params=params)
            response.raise_for_status()
            parsed = URLScanioResponse.parse_raw(response.text)
            
            for result in parsed.results:
                if is_malicious(result):
                    return URLResponse(
                        domain=domain,
                        malicious=True,
                        info=f"Detectado como sospechoso. Fuente: {result.task.source or 'Desconocida'}",
                        source="URLScan.io"
                    )

            return URLResponse(
                domain=domain,
                malicious=False,
                info="Seguro. No se detectaron señales de phishing",
                source="URLScan.io"
            )
        
    except httpx.RequestError as e:
        return URLResponse(
            domain=domain,
            malicious=False,
            info=f"Error de conexión: {str(e)}",
            source="URLScan.io"
        )
    
    except httpx.HTTPStatusError as e:
        return URLResponse(
            domain=domain,
            malicious=False,
            info=f"Error HTTP {e.response.status_code}: {e.response.text}",
            source="URLScan.io"
        )

    except Exception as e:
        return URLResponse(
            domain=domain,
            malicious=False,
            info=f"Error inesperado: {str(e)}",
            source="URLScan.io"
        )