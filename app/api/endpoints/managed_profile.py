"""
API endpoints para la gestión de perfiles gestionados.

Este módulo define las rutas para crear, leer, actualizar y eliminar (CRUD)
perfiles gestionados, así como para vincularlos con extensiones.
Los perfiles gestionados están asociados a un usuario "manager" que los controla.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.core.security import get_current_user
from app.models.user_model import User
from app.models.managed_profile_model import (
    ManagedProfileCreate,
    ManagedProfileRead, 
    ManagedProfileUpdate,
    LinkExtensionRequest
)
from app.api.services import managed_profile_service
from app.database import get_session

router = APIRouter()

@router.post("/", response_model=ManagedProfileRead, status_code=status.HTTP_201_CREATED, tags=["Perfiles Gestionados"])
async def create_new_managed_profile(
    profile_in: ManagedProfileCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Crea un nuevo perfil gestionado para el usuario manager autenticado.

    :param profile_in: Datos para la creación del perfil gestionado.
    :type profile_in: ManagedProfileCreate
    :param session: Sesión de base de datos.
    :type session: Session
    :param current_user: Usuario manager autenticado.
    :type current_user: User
    :return: El perfil gestionado creado.
    :rtype: ManagedProfileRead
    """

    created_profile = await managed_profile_service.create_managed_profile(
        session=session,
        managed_profile_in=profile_in,
        manager_user_id=current_user.id
    )
    return created_profile


@router.put("/{profile_id}", response_model=ManagedProfileRead, tags=["Perfiles Gestionados"])
async def update_existing_managed_profile(
    profile_id: int,
    profile_update: ManagedProfileUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza un perfil gestionado existente.

    Solo el manager propietario del perfil puede actualizarlo.

    :param profile_id: ID del perfil gestionado a actualizar.
    :type profile_id: int
    :param profile_update: Datos para actualizar el perfil gestionado.
    :type profile_update: ManagedProfileUpdate
    :param session: Sesión de base de datos.
    :type session: Session
    :param current_user: Usuario manager autenticado.
    :type current_user: User
    :raises HTTPException: Si el perfil no se encuentra, el usuario no está autorizado,
                           o si hay un nombre de perfil duplicado.
    :return: El perfil gestionado actualizado.
    :rtype: ManagedProfileRead
    """
    updated_profile = await managed_profile_service.update_managed_profile(
        session=session,
        profile_id=profile_id,
        managed_profile_update=profile_update,
        manager_user_id=current_user.id
    )
    if not updated_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado, no autorizado, o nombre de perfil duplicado.")
    return updated_profile

@router.get("/", response_model=List[ManagedProfileRead], tags=["Perfiles Gestionados"])
async def read_managed_profiles_for_current_user(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene todos los perfiles gestionados por el usuario manager autenticado,
    incluyendo el conteo de reglas de bloqueo para cada perfil.

    :param session: Sesión de base de datos.
    :type session: Session
    :param current_user: Usuario manager autenticado.
    :type current_user: User
    :return: Lista de perfiles gestionados por el usuario con conteo de reglas.
    :rtype: List[ManagedProfileRead]
    """
    profiles_db = await managed_profile_service.get_managed_profiles_by_manager(
        session=session, manager_user_id=current_user.id
    )
    
    response_profiles = []
    for profile_db in profiles_db:
        rules_count = len(profile_db.blocking_rules) 
        
        profile_read_data = profile_db.model_dump()
        profile_read_data['blocking_rules_count'] = rules_count
        
        response_profiles.append(ManagedProfileRead.model_validate(profile_read_data))
        
    return response_profiles

@router.get("/{profile_id}", response_model=ManagedProfileRead, tags=["Perfiles Gestionados"])
async def read_managed_profile_by_id(
    profile_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene un perfil gestionado específico por su ID.

    Asegura que el perfil pertenece al usuario manager autenticado.

    :param profile_id: ID del perfil gestionado a obtener.
    :type profile_id: int
    :param session: Sesión de base de datos.
    :type session: Session
    :param current_user: Usuario manager autenticado.
    :type current_user: User
    :raises HTTPException: Si el perfil no se encuentra o el usuario no está autorizado.
    :return: El perfil gestionado solicitado.
    :rtype: ManagedProfileRead
    """
    profile = await managed_profile_service.get_managed_profile_by_id_and_manager(
        session=session, profile_id=profile_id, manager_user_id=current_user.id
    )
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado o no autorizado.")
    return profile

@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Perfiles Gestionados"])
async def delete_existing_managed_profile(
    profile_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina un perfil gestionado existente.

    Solo el manager propietario del perfil puede eliminarlo.

    :param profile_id: ID del perfil gestionado a eliminar.
    :type profile_id: int
    :param session: Sesión de base de datos.
    :type session: Session
    :param current_user: Usuario manager autenticado.
    :type current_user: User
    :raises HTTPException: Si el perfil no se encuentra o el usuario no está autorizado.
    :return: None.
    :rtype: None
    """
    deleted_profile = await managed_profile_service.delete_managed_profile(
        session=session,
        profile_id=profile_id,
        manager_user_id=current_user.id
    )
    if not deleted_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado o no autorizado.")
    return None

@router.post("/link-extension", response_model=ManagedProfileRead, tags=["Perfiles Gestionados - Extensión"])
async def link_extension(
    link_request: LinkExtensionRequest,
    session: Session = Depends(get_session)
):
    """
    Vincula una extensión a un perfil gestionado utilizando un código de vinculación.

    Este endpoint es utilizado por la extensión del navegador para asociarse
    con un perfil gestionado existente a través de un código único.

    :param link_request: Datos para la vinculación de la extensión,
                         incluyendo el código de vinculación.
    :type link_request: LinkExtensionRequest
    :param session: Sesión de base de datos.
    :type session: Session
    :raises HTTPException: Si el código de vinculación no es válido o el perfil no se encuentra.
    :return: El perfil gestionado ahora vinculado con la extensión.
    :rtype: ManagedProfileRead
    """
    linked_profile = await managed_profile_service.link_extension_to_profile(
        session=session,
        link_request=link_request
    )
    return linked_profile