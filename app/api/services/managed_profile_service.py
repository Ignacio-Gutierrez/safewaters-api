from sqlmodel import Session
from typing import List, Optional
from fastapi import HTTPException, status
import secrets 
from datetime import datetime

from app.models.managed_profile_model import (
    ManagedProfile,
    ManagedProfileCreate,
    ManagedProfileUpdate,
    LinkExtensionRequest
)
from app.crud import crud_managed_profile

from app.config import settings

LINK_CODE_LENGTH_BYTES = settings.LINK_CODE_LENGTH_BYTES

async def create_managed_profile(
    session: Session,
    managed_profile_in: ManagedProfileCreate,
    manager_user_id: int
) -> ManagedProfile:
    """
    Crea un nuevo perfil gestionado para un usuario manager.

    Verifica que el nombre del perfil sea único para el manager.
    Genera un código de enlace único.

    :param session: La sesión de base de datos.
    :type session: Session
    :param managed_profile_in: Datos para crear el perfil.
    :type managed_profile_in: ManagedProfileCreate
    :param manager_user_id: ID del usuario manager propietario.
    :type manager_user_id: int
    :return: El perfil gestionado creado.
    :rtype: ManagedProfile
    :raises HTTPException: Si ya existe un perfil con el mismo nombre para este manager (HTTP 400).
    """
    existing_profile = crud_managed_profile.get_managed_profile_by_name_and_manager_id(
        session=session, profile_name=managed_profile_in.profile_name, manager_id=manager_user_id
    )
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un perfil con este nombre para este usuario."
        )

    link_code = secrets.token_urlsafe(LINK_CODE_LENGTH_BYTES)

    while crud_managed_profile.get_managed_profile_by_link_code(session, link_code):
        link_code = secrets.token_urlsafe(LINK_CODE_LENGTH_BYTES)

    profile_data_for_db = managed_profile_in.model_dump(
        exclude={"link_status", "manager_user_id", "link_code", "extension_instance_id", "created_at", "id"}
    )
    
    profile_to_create = ManagedProfile(
        **profile_data_for_db,
        manager_user_id=manager_user_id,
        link_code=link_code,
        link_status='waiting_for_link'
    )
    return crud_managed_profile.create_managed_profile_db(session=session, profile_to_create=profile_to_create)


async def get_managed_profiles_by_manager(
    session: Session,
    manager_user_id: int
) -> List[ManagedProfile]:
    """
    Obtiene todos los perfiles gestionados para un usuario manager específico.

    :param session: La sesión de base de datos.
    :type session: Session
    :param manager_user_id: ID del usuario manager.
    :type manager_user_id: int
    :return: Una lista de perfiles gestionados pertenecientes al manager.
    :rtype: List[ManagedProfile]
    """
    return crud_managed_profile.get_managed_profiles_by_manager_id(session=session, manager_id=manager_user_id)

async def get_managed_profile_by_id_and_manager(
    session: Session,
    profile_id: int,
    manager_user_id: int
) -> Optional[ManagedProfile]:
    """
    Obtiene un perfil gestionado específico por su ID, asegurando que pertenece al manager especificado.

    :param session: La sesión de base de datos.
    :type session: Session
    :param profile_id: ID del perfil a obtener.
    :type profile_id: int
    :param manager_user_id: ID del usuario manager propietario.
    :type manager_user_id: int
    :return: El perfil gestionado si se encuentra y pertenece al manager, de lo contrario None.
    :rtype: Optional[ManagedProfile]
    """
    profile = crud_managed_profile.get_managed_profile_by_id(session=session, profile_id=profile_id)
    if profile and profile.manager_user_id == manager_user_id:
        return profile
    return None

async def update_managed_profile(
    session: Session,
    profile_id: int,
    managed_profile_update: ManagedProfileUpdate,
    manager_user_id: int
) -> Optional[ManagedProfile]:
    """
    Actualiza un perfil gestionado existente.

    Solo el manager propietario del perfil puede actualizarlo.
    Si se intenta cambiar el nombre del perfil, se verifica que el nuevo nombre no
    esté ya en uso por otro perfil del mismo manager.

    :param session: La sesión de base de datos.
    :type session: Session
    :param profile_id: ID del perfil a actualizar.
    :type profile_id: int
    :param managed_profile_update: Datos para actualizar el perfil.
    :type managed_profile_update: ManagedProfileUpdate
    :param manager_user_id: ID del usuario manager propietario.
    :type manager_user_id: int
    :return: El perfil gestionado actualizado, o None si el perfil no se encuentra o no pertenece al manager.
    :rtype: Optional[ManagedProfile]
    :raises HTTPException: Si el nuevo nombre de perfil ya existe para este manager (HTTP 400).
    """
    db_profile = await get_managed_profile_by_id_and_manager(
        session=session, profile_id=profile_id, manager_user_id=manager_user_id
    )
    if not db_profile:
        return None 

    update_data = managed_profile_update.model_dump(exclude_unset=True)

    if "profile_name" in update_data and update_data["profile_name"] != db_profile.profile_name:
        existing_profile_with_new_name = crud_managed_profile.get_managed_profile_by_name_and_manager_id(
            session=session, profile_name=update_data["profile_name"], manager_id=manager_user_id
        )
        if existing_profile_with_new_name and existing_profile_with_new_name.id != profile_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro perfil con este nuevo nombre para este usuario."
            )
    
    return crud_managed_profile.update_managed_profile_db(
        session=session, db_profile=db_profile, profile_update_data=managed_profile_update
    )

async def delete_managed_profile(
    session: Session,
    profile_id: int,
    manager_user_id: int
) -> Optional[ManagedProfile]:
    """
    Elimina un perfil gestionado existente.

    Solo el manager propietario del perfil puede eliminarlo.

    :param session: La sesión de base de datos.
    :type session: Session
    :param profile_id: ID del perfil a eliminar.
    :type profile_id: int
    :param manager_user_id: ID del usuario manager propietario.
    :type manager_user_id: int
    :return: El perfil gestionado que fue eliminado, o None si no se encontró o no pertenecía al manager.
    :rtype: Optional[ManagedProfile]
    """
    profile_to_delete = await get_managed_profile_by_id_and_manager(
        session=session, profile_id=profile_id, manager_user_id=manager_user_id
    )
    if not profile_to_delete:
        return None

    return crud_managed_profile.delete_managed_profile_db(session=session, profile_id=profile_id)


async def link_extension_to_profile(
    session: Session,
    link_request: LinkExtensionRequest
) -> Optional[ManagedProfile]:
    """
    Vincula una instancia de extensión a un perfil gestionado utilizando un código de enlace.

    Este servicio es utilizado por el endpoint que la extensión del navegador consume.
    Verifica la validez del código de enlace. Si es válido, actualiza el perfil
    gestionado para marcarlo como 'linked', almacena el `extension_instance_id`
    y elimina el `link_code` para que no pueda ser reutilizado.
    También actualiza `last_extension_communication`.

    Maneja los casos donde:
    - El código de enlace es inválido.
    - El perfil ya está vinculado a una instancia de extensión diferente.
    - La instancia de extensión ya está vinculada a un perfil diferente.

    :param session: La sesión de base de datos.
    :type session: Session
    :param link_request: Objeto con el `link_code` y `extension_instance_id`.
    :type link_request: LinkExtensionRequest
    :return: El perfil gestionado actualizado después de la vinculación.
    :rtype: Optional[ManagedProfile]
    :raises HTTPException:
        - 400 (Bad Request): Si el código de enlace es inválido o ha expirado.
        - 409 (Conflict): Si el perfil ya está vinculado a otra instancia de extensión.
        - 409 (Conflict): Si la instancia de extensión ya está vinculada a otro perfil.
    """

    profile = crud_managed_profile.get_managed_profile_by_link_code(
        session=session, link_code=link_request.link_code
    )

    if not profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Código de enlace inválido o expirado.")
    
    if profile.link_status == 'linked' and \
       profile.extension_instance_id is not None and \
       profile.extension_instance_id != link_request.extension_instance_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este perfil ya está vinculado a otra instancia de extensión."
        )
    
    existing_profile_for_extension = crud_managed_profile.get_managed_profile_by_extension_instance_id(
        session=session, extension_instance_id=link_request.extension_instance_id
    )
    if existing_profile_for_extension and existing_profile_for_extension.id != profile.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta instancia de extensión ya está vinculada a otro perfil."
        )
    
    profile.extension_instance_id = link_request.extension_instance_id
    profile.link_status = 'linked'
    profile.link_code = None
    profile.last_extension_communication = datetime.utcnow()
    
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile