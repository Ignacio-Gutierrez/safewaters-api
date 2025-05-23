"""
Módulo de servicios para gestionar el historial de navegación.

Este módulo proporciona funciones para registrar visitas de navegación y
recuperar el historial de navegación de un perfil específico, asegurando
las comprobaciones de autorización necesarias.
"""
from typing import List, Optional
from sqlmodel import Session
from fastapi import HTTPException, status

from app.crud import crud_navigation_history as crud_nav_history
from app.crud import crud_managed_profile
from app.models.navigation_history_model import NavigationHistory, NavigationHistoryCreate, NavigationHistoryRead
from app.models.user_model import User

async def record_navigation_visit(
    session: Session,
    profile_id: int,
    url: str,
) -> NavigationHistory:
    """
    Registra una visita de navegación para un perfil.

    Este servicio crea una nueva entrada en el historial de navegación
    asociada con el `profile_id` proporcionado.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param profile_id: El ID del perfil para el cual se registra la visita.
    :type profile_id: int
    :param url: La URL visitada.
    :type url: str
    :return: El objeto de historial de navegación creado.
    :rtype: app.models.navigation_history_model.NavigationHistory
    """
    history_create = NavigationHistoryCreate(
        visited_url=url,
    )
    
    return await crud_nav_history.create_navigation_history_entry(
        session=session,
        history_entry=history_create,
        profile_id=profile_id
    )

async def get_profile_navigation_history(
    session: Session,
    profile_id: int,
    current_user: User,
    skip: int = 0,
    limit: int = 100
) -> List[NavigationHistoryRead]:
    """
    Obtiene el historial de navegación para un perfil específico.

    Verifica que el `current_user` sea el propietario del perfil antes de
    devolver el historial.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param profile_id: El ID del perfil cuyo historial se va a recuperar.
    :type profile_id: int
    :param current_user: El usuario autenticado que realiza la solicitud.
    :type current_user: app.models.user_model.User
    :param skip: Número de registros a omitir (para paginación).
    :type skip: int
    :param limit: Número máximo de registros a devolver (para paginación).
    :type limit: int
    :return: Una lista de entradas del historial de navegación.
    :rtype: List[app.models.navigation_history_model.NavigationHistoryRead]
    :raises HTTPException: Si el perfil no se encuentra (404) o si el usuario
                           no está autorizado para acceder al historial (403).
    """
    profile = crud_managed_profile.get_managed_profile_by_id(session=session, profile_id=profile_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado")
        
    if profile.manager_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para acceder a este historial")

    history_db = await crud_nav_history.get_navigation_history_for_profile(
        session=session, profile_id=profile_id, skip=skip, limit=limit
    )
    return [NavigationHistoryRead.model_validate(entry) for entry in history_db]
