"""
Módulo de rutas para la API de SafeWaters.

Define los endpoints de la API, incluyendo ``/check`` para la verificación de URLs
y el registro de navegación asociado.
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.schemas.urls_check import URLRequest, URLResponse
from app.api.services.url_check_service import check_url as service_check_url
from app.database import get_session

from app.crud import crud_managed_profile
from app.api.services import navigation_history_service

router = APIRouter()
"""
Instancia de :class:`fastapi.APIRouter` para registrar las rutas de la API.
"""

@router.post("/check", response_model=URLResponse, tags=["Detección"])
async def check(
    request: URLRequest,
    session: Session = Depends(get_session)
):
    """
    Endpoint para verificar una URL, determinar si es maliciosa y registrar la navegación.

    Recibe una URL en el cuerpo de la solicitud y la procesa utilizando el servicio
    :func:`app.api.services.url_check_service.check_url`.
    Si se proporciona un `extension_instance_id` en la solicitud, también se
    intenta registrar la visita en el historial de navegación del perfil gestionado asociado.

    :param request: Objeto de solicitud que contiene la URL a verificar.
                    Puede incluir `extension_instance_id` y `page_title`.
    :type request: app.schemas.urls_check.URLRequest
    :param session: Sesión de base de datos inyectada.
    :type session: sqlmodel.Session
    :return: Un objeto con la información de la verificación, incluyendo si es maliciosa,
             información adicional y la fuente de la detección.
    :rtype: app.schemas.urls_check.URLResponse
    :raises HTTPException: Si ocurre un error durante el procesamiento de la URL.
    """
    analysis_result: URLResponse = await service_check_url(str(request.url))

    if request.extension_instance_id:
        profile = crud_managed_profile.get_managed_profile_by_extension_instance_id(
            session=session, extension_instance_id=request.extension_instance_id
        )
        
        if profile and profile.id is not None:
            try:
                await navigation_history_service.record_navigation_visit(
                    session=session,
                    profile_id=profile.id,
                    url=str(request.url),
                    page_title=request.page_title
                )
            except Exception as e:
                pass
    return analysis_result