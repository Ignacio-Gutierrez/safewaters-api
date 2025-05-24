"""
Módulo de rutas para el historial de navegación de perfiles gestionados.

Define los endpoints de la API para acceder al historial de navegación
asociado a los perfiles gestionados por los usuarios.
"""
from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.api.services import navigation_history_service as nav_history_service
from app.models.navigation_history_model import NavigationHistoryRead
from app.models.user_model import User
from app.core.security import get_current_user
from app.models.pagination_model import PaginatedResponse

router = APIRouter()
"""
Instancia de :class:`fastapi.APIRouter` para registrar las rutas relacionadas con el historial de navegación.
"""

@router.get(
    "/{profile_id}/history",
    response_model=PaginatedResponse[NavigationHistoryRead],
    tags=["Historial de Navegación"],
    summary="Obtener historial de navegación para un perfil gestionado"
)
async def read_navigation_history_for_profile(
    profile_id: int,
    page: int = Query(1, ge=1, description="Número de página a recuperar, comenzando desde 1."),
    page_size: int = Query(10, ge=1, le=100, description="Número de elementos por página."),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> PaginatedResponse[NavigationHistoryRead]:
    """
    Obtiene el historial de navegación paginado para un perfil gestionado específico.

    El usuario autenticado debe ser el propietario del perfil para poder acceder
    a esta información. La paginación se controla con los parámetros `page` y `page_size`.

    :param profile_id: El ID del perfil gestionado cuyo historial se desea obtener.
    :type profile_id: int
    :param page: Número de página a recuperar.
    :type page: int
    :param page_size: Número de elementos por página.
    :type page_size: int
    :param session: Sesión de base de datos inyectada.
    :type session: sqlmodel.Session
    :param current_user: El usuario autenticado que realiza la solicitud.
    :type current_user: app.models.user_model.User
    :return: Un objeto PaginatedResponse con los datos de paginación y la lista de entradas del historial.
    :rtype: app.models.pagination_model.PaginatedResponse[app.models.navigation_history_model.NavigationHistoryRead]
    :raises HTTPException: Si el perfil no se encuentra (404), si el usuario
                           no está autorizado (403), o si la página solicitada está fuera de rango (404).
                           Estas excepciones son propagadas desde el servicio.
    """
    paginated_history = await nav_history_service.get_profile_navigation_history(
        session=session,
        profile_id=profile_id,
        current_user=current_user,
        page=page,
        page_size=page_size
    )
    return paginated_history
