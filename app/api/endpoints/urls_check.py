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
                    Puede incluir `extension_instance_id`.
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
            block_check_result = await blocking_rule_service.check_blocking_rules(
                session=session,
                profile_id=managed_profile.id,
                url=str(request.url)
            )
            if block_check_result["is_blocked"]:
                # CASO 1: URL BLOQUEADA POR REGLA DE USUARIO
                url_domain = get_domain_from_url(str(request.url)) or "N/A"
                response_data_blocked_by_user = URLResponse(
                    domain=url_domain,
                    malicious=False, # No es maliciosa por análisis externo, sino bloqueada por usuario
                    info=block_check_result["reason"] or "Bloqueado por regla de usuario.",
                    source="User Defined Rule",
                    is_blocked_by_user_rule=True,
                    blocking_rule_details=block_check_result["reason"]
                )

                try:
                    # Registrar intento de navegación
                    await navigation_history_service.record_navigation_visit(
                        session=session,
                        profile_id=profile_id_for_nav_history,
                        url=str(request.url)
                        # Los campos is_malicious e is_blocked_by_user se eliminan 
                        # según el error del log anterior.
                    )
                except Exception as e:
                    print(f"Error al registrar navegación para URL bloqueada por usuario: {e}")
                    # Considerar logging en producción
                    pass 

                return response_data_blocked_by_user # Retornar aquí y no continuar
        
    # CASO 2: URL NO BLOQUEADA POR REGLA DE USUARIO (o no hay perfil/reglas aplicables)
    # Proceder con el análisis de seguridad externo
    analysis_result_dict = await service_check_url(str(request.url))
    
    # Construir la respuesta final basada en el análisis externo
    # El response_model URLResponse sí espera is_blocked_by_user_rule y blocking_rule_details
    # por lo que los mantenemos aquí, reflejando el estado actual.
    final_response = URLResponse(
        domain=analysis_result_dict["domain"],
        malicious=analysis_result_dict["malicious"],
        info=analysis_result_dict["info"],
        source=analysis_result_dict["source"],
        is_blocked_by_user_rule=False, # En este camino, no fue bloqueada por regla de usuario
        blocking_rule_details=None
    )

    # Registrar la visita en el historial de navegación (si se identificó un perfil)
    if profile_id_for_nav_history:
        try:
            await navigation_history_service.record_navigation_visit(
                session=session,
                profile_id=profile_id_for_nav_history,
                url=str(request.url)
                # Los campos is_malicious e is_blocked_by_user se eliminan
                # según el error del log anterior.
            )
        except Exception as e:
            print(f"Error al registrar navegación para URL analizada externamente: {e}")
            # Considerar logging en producción
            pass 
            
    return final_response