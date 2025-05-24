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
from app.models.pagination_model import PaginatedResponse 

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
    page: int,
    page_size: int
) -> PaginatedResponse[NavigationHistoryRead]:
    """
    Obtiene el historial de navegación paginado para un perfil específico.

    Verifica que el `current_user` sea el propietario del perfil antes de
    devolver el historial.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param profile_id: El ID del perfil cuyo historial se va a recuperar.
    :type profile_id: int
    :param current_user: El usuario autenticado que realiza la solicitud.
    :type current_user: app.models.user_model.User
    :param page: Número de página a recuperar.
    :type page: int
    :param page_size: Número de elementos por página.
    :type page_size: int
    :return: Un objeto PaginatedResponse con el historial de navegación.
    :rtype: app.models.pagination_model.PaginatedResponse[app.models.navigation_history_model.NavigationHistoryRead]
    :raises HTTPException: Si el perfil no se encuentra (404), si el usuario
                           no está autorizado (403), o si la página solicitada está fuera de rango (404).
    """
    profile = crud_managed_profile.get_managed_profile_by_id(session=session, profile_id=profile_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado")
        
    if profile.manager_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para acceder a este historial")

    skip = (page - 1) * page_size
    limit = page_size

    history_db_items = await crud_nav_history.get_navigation_history_for_profile(
        session=session, profile_id=profile_id, skip=skip, limit=limit
    )
    
    total_items = await crud_nav_history.count_navigation_history_for_profile(
        session=session, profile_id=profile_id
    )

    total_pages = 0
    if page_size > 0:
        total_pages = (total_items + page_size - 1) // page_size
    elif total_items > 0 :
        total_pages = 1 
    
    if total_items == 0:
        total_pages = 0
    elif total_pages == 0 and total_items > 0:
        total_pages = 1


    if total_items == 0 and page != 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Página {page} no encontrada. No hay historial de navegación."
        )
    
    if total_items > 0 and page > total_pages:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Página {page} no encontrada. Hay {total_pages} páginas en total."
        )

    return PaginatedResponse[NavigationHistoryRead](
        total_items=total_items,
        total_pages=total_pages if total_items > 0 else 0,
        current_page=page,
        page_size=page_size,
        items=[NavigationHistoryRead.model_validate(entry) for entry in history_db_items]
    )