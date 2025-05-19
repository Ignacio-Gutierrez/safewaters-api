"""
Módulo para interactuar con la API de URLScan.io.

Este módulo proporciona funciones para consultar la API de URLScan.io y verificar
si un dominio ha sido reportado o etiquetado como malicioso en escaneos recientes.
Utiliza la configuración de la aplicación para obtener la clave API y la URL base del servicio.
"""
from app.config import settings
import httpx

from app.models.urls import URLResponse
from app.utils.external_api_models.urlscanio_model import URLScanioResponse, ResultItem

URLSCANIO_API_KEY = settings.URLSCANIO_API_KEY
URLSCANIO_API_URL = settings.URLSCANIO_API_URL

def is_malicious(result: ResultItem) -> bool:
    """
    Determina si un resultado de escaneo de URLScan.io se considera malicioso.

    Un resultado se considera malicioso si alguna de sus etiquetas (``result.task.tags``)
    contiene la subcadena "phish" (insensible a mayúsculas/minúsculas), o si su
    fuente (``result.task.source``) contiene "phish" o "suspicious"
    (insensible a mayúsculas/minúsculas).

    :param result: El ítem de resultado del escaneo de URLScan.io.
    :type result: app.models.url_urlscanio.ResultItem
    :return: ``True`` si el resultado se considera malicioso, ``False`` en caso contrario.
    :rtype: bool
    """
    tags = result.task.tags or []
    source = (result.task.source or "").lower()
    return any("phish" in tag.lower() for tag in tags) or "phish" in source or "suspicious" in source


async def check_urlscanio(domain: str) -> URLResponse:
    """
    Consulta URLScan.io de forma asincrónica con un dominio y devuelve los datos relevantes.

    Realiza una búsqueda en URLScan.io para escaneos relacionados con el dominio especificado
    en los últimos 90 días. Si alguno de los resultados se considera malicioso
    según la función :func:`is_malicious`, se devuelve una respuesta indicando
    que el dominio es malicioso.

    :param domain: El dominio a verificar.
    :type domain: str
    :return: Un objeto :class:`~app.models.urls.URLResponse` con el resultado de la verificación.
             El objeto devuelto tiene los siguientes atributos importantes:
             - Si se encuentra un escaneo malicioso, ``malicious`` será ``True``.
             - Si no se encuentran escaneos maliciosos o no hay resultados, ``malicious`` será ``False``.
             - En caso de error (conexión, HTTP, u otro), ``malicious`` será ``False`` y ``info`` contendrá el mensaje de error.
    :rtype: app.models.urls.URLResponse
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
                        info=f"Detectado como sospechoso/phishing en URLScan.io. Fuente del escaneo: {result.task.source or 'Desconocida'}. Tags: {result.task.tags}",
                        source="URLScan.io"
                    )
            return URLResponse(
                domain=domain,
                malicious=False,
                info=f"Dominio '{domain}' no encontrado como malicioso en escaneos recientes de URLScan.io.",
                source="URLScan.io"
            )
        
    except httpx.RequestError as e:
        return URLResponse(
            domain=domain,
            malicious=False,
            info=f"Error de conexión con URLScan.io para '{domain}': {str(e)}",
            source="URLScan.io"
        )
    
    except httpx.HTTPStatusError as e:
        return URLResponse(
            domain=domain,
            malicious=False,
            info=f"Error HTTP {e.response.status_code} de URLScan.io para '{domain}': {e.response.text}",
            source="URLScan.io"
        )

    except Exception as e:
        return URLResponse(
            domain=domain,
            malicious=False,
            info=f"Error inesperado al procesar respuesta de URLScan.io para '{domain}': {str(e)}",
            source="URLScan.io"
        )