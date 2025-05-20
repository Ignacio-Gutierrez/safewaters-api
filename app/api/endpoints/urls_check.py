"""
Módulo de rutas para la API de SafeWaters.

Define los endpoints de la API, actualmente solo incluye el endpoint ``/check``
para la verificación de URLs.
"""
from fastapi import APIRouter
from app.schemas.urls_check import URLRequest, URLResponse
from app.api.services import check_url

router = APIRouter()
"""
Instancia de :class:`fastapi.APIRouter` para registrar las rutas de la API.
"""

@router.post("/check", response_model=URLResponse, tags=["Detección"])
async def check(request: URLRequest):
    """
    Endpoint para verificar una URL y determinar si es maliciosa.

    Recibe una URL en el cuerpo de la solicitud y la procesa utilizando el servicio
    :func:`app.api.services.check_url`.

    :param request: Objeto de solicitud que contiene la URL a verificar.
    :type request: app.models.urls.URLRequest
    :return: Un objeto con la información de la verificación, incluyendo si es maliciosa,
             información adicional y la fuente de la detección.
    :rtype: app.models.urls.URLResponse
    :raises HTTPException: Si ocurre un error durante el procesamiento de la URL.
    """
    return await check_url(str(request.url))