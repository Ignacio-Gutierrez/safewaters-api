"""
Módulo de rutas para la API de SafeWaters.

Define los endpoints de la API, incluyendo ``/check`` para la verificación de URLs
y el registro de navegación asociado.
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.schemas.urls_check import URLRequest, URLResponse
from app.api.services.url_check_service import check_url as service_check_url
from app.utils.domain_utils import get_domain_from_url
from app.database import get_session

from app.crud import crud_managed_profile
from app.api.services import navigation_history_service
from app.api.services import blocking_rule_service

from typing import Dict, Any, Optional

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
    Endpoint para verificar una URL.
    Primero comprueba si está bloqueada por reglas del usuario.
    Si no está bloqueada por el usuario, determina si es maliciosa según fuentes externas.
    Finalmente, registra la navegación.

    :param request: Objeto de solicitud que contiene la URL a verificar.
                    Puede incluir `extension_instance_id` y `page_title`.
    :type request: app.schemas.urls_check.URLRequest
    :param session: Sesión de base de datos inyectada.
    :type session: sqlmodel.Session
    :return: Un objeto con la información de la verificación.
    :rtype: app.schemas.urls_check.URLResponse
    :raises HTTPException: Si ocurre un error durante el procesamiento de la URL.
    """

    profile_id_for_nav_history: Optional[int] = None

    # 1. Verificar si hay un perfil y si la URL está bloqueada por reglas del usuario
    if request.extension_instance_id:
        managed_profile = crud_managed_profile.get_managed_profile_by_extension_instance_id(
            session=session, extension_instance_id=request.extension_instance_id
        )
        
        if managed_profile and managed_profile.id is not None:
            profile_id_for_nav_history = managed_profile.id
            block_check_result = await blocking_rule_service.create_blocking_rule_for_profile_service(
                session=session,
                profile_id=managed_profile.id,
                url=str(request.url)
            )
            if block_check_result["is_blocked"]:
                url_domain = get_domain_from_url(str(request.url)) or "N/A"
                response_data = URLResponse(
                    domain=url_domain,
                    malicious=False,
                    info=block_check_result["reason"] or "Bloqueado por regla de usuario.",
                    source="User Defined Rule",
                    is_blocked_by_user_rule=True,
                    blocking_rule_details=block_check_result["reason"]
                )

            try:
                await navigation_history_service.record_navigation_visit(
                    session=session,
                    profile_id=profile_id_for_nav_history,
                    url=str(request.url),
                    is_malicious=response_data.malicious,
                    is_blocked_by_user=response_data.is_blocked_by_user_rule
                )
            except Exception as e:
                pass

            return response_data
        

    # 2. Si no está bloqueado por el usuario (o no hay perfil), proceder con el análisis de seguridad externo
    analysis_result_dict = await service_check_url(str(request.url))
    
    final_response = URLResponse(
        domain=analysis_result_dict["domain"],
        malicious=analysis_result_dict["malicious"],
        info=analysis_result_dict["info"],
        source=analysis_result_dict["source"],
        is_blocked_by_user_rule=False,
        blocking_rule_details=None
    )

    # 3. Registrar la visita en el historial de navegación (si hay perfil)
    if profile_id_for_nav_history:
        try:
            await navigation_history_service.record_navigation_visit(
                session=session,
                profile_id=profile_id_for_nav_history,
                url=str(request.url),
                page_title=request.page_title,
                is_malicious=final_response.malicious,
                is_blocked_by_user=final_response.is_blocked_by_user_rule
            )
        except Exception as e:

            pass 
            
    return final_response