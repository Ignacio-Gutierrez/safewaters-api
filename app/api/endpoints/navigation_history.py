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

router = APIRouter()
"""
Instancia de :class:`fastapi.APIRouter` para registrar las rutas relacionadas con el historial de navegación.
"""

@router.get(
    "/{profile_id}/history",
    response_model=List[NavigationHistoryRead],
    tags=["Historial de Navegación"],
    summary="Obtener historial de navegación para un perfil gestionado"
)
async def read_navigation_history_for_profile(
    profile_id: int,
    skip: int = Query(0, ge=0, description="Número de registros a saltar para paginación."),
    limit: int = Query(100, ge=1, le=200, description="Número máximo de registros a devolver por página."),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> List[NavigationHistoryRead]:
    """
    Obtiene el historial de navegación para un perfil gestionado específico.

    El usuario autenticado debe ser el propietario del perfil para poder acceder
    a esta información. La paginación se controla con los parámetros `skip` y `limit`.

    :param profile_id: El ID del perfil gestionado cuyo historial se desea obtener.
    :type profile_id: int
    :param skip: Número de registros a omitir (para paginación).
    :type skip: int
    :param limit: Número máximo de registros a devolver (para paginación).
    :type limit: int
    :param session: Sesión de base de datos inyectada.
    :type session: sqlmodel.Session
    :param current_user: El usuario autenticado que realiza la solicitud.
                         Se utiliza para verificar la propiedad del perfil.
    :type current_user: app.models.user_model.User
    :return: Una lista de entradas del historial de navegación para el perfil especificado.
    :rtype: List[app.models.navigation_history_model.NavigationHistoryRead]
    :raises HTTPException: Si el perfil no se encuentra (404) o si el usuario
                           no está autorizado para acceder al historial (403),
                           estas excepciones son propagadas desde el servicio.
    """
    history = await nav_history_service.get_profile_navigation_history(
        session=session,
        profile_id=profile_id,
        current_user=current_user,
        skip=skip,
        limit=limit
    )
    return history
