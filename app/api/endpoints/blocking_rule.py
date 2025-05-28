"""
Módulo de rutas para las reglas de bloqueo de perfiles gestionados.

Define los endpoints de la API para crear, leer, actualizar y eliminar
reglas de bloqueo asociadas a los perfiles gestionados por los usuarios.
"""
from typing import List

from fastapi import APIRouter, Depends, status, Query
from sqlmodel import Session

from app.database import get_session
from app.api.services import blocking_rule_service
from app.models.blocking_rule_model import (
    BlockingRuleCreate,
    BlockingRuleRead,
    BlockingRuleUpdate,
)
from app.models.user_model import User
from app.core.security import get_current_user

router = APIRouter()
"""
Instancia de :class:`fastapi.APIRouter` para registrar las rutas relacionadas con las reglas de bloqueo.
"""

@router.post(
    "/managed-profiles/{managed_profile_id}/blocking-rules/",
    response_model=BlockingRuleRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Reglas de Bloqueo"],
    summary="Crear una nueva regla de bloqueo para un perfil gestionado"
)
def create_blocking_rule_for_managed_profile(
    managed_profile_id: int,
    blocking_rule_in: BlockingRuleCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> BlockingRuleRead:
    """
    Crea una nueva regla de bloqueo para un perfil gestionado específico.

    El usuario autenticado debe ser el propietario del perfil gestionado.

    :param managed_profile_id: El ID del perfil gestionado para el cual se crea la regla.
    :type managed_profile_id: int
    :param blocking_rule_in: Los datos para la nueva regla de bloqueo.
    :type blocking_rule_in: app.models.blocking_rule_model.BlockingRuleCreate
    :param session: Sesión de base de datos inyectada.
    :type session: sqlmodel.Session
    :param current_user: El usuario autenticado que realiza la solicitud.
    :type current_user: app.models.user_model.User
    :return: La regla de bloqueo creada.
    :rtype: app.models.blocking_rule_model.BlockingRuleRead
    :raises HTTPException: Propagada desde el servicio si el perfil no se encuentra (404)
                           o el usuario no está autorizado (403).
    """
    return blocking_rule_service.create_blocking_rule_for_profile_service(
        session=session,
        managed_profile_id=managed_profile_id,
        blocking_rule_in=blocking_rule_in,
        current_user=current_user,
    )

@router.get(
    "/managed-profiles/{managed_profile_id}/blocking-rules/",
    response_model=List[BlockingRuleRead],
    tags=["Reglas de Bloqueo"],
    summary="Obtener todas las reglas de bloqueo para un perfil gestionado"
)
def read_blocking_rules_for_managed_profile(
    managed_profile_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[BlockingRuleRead]:
    """
    Obtiene todas las reglas de bloqueo para un perfil gestionado específico.

    El usuario autenticado debe ser el propietario del perfil.

    :param managed_profile_id: El ID del perfil gestionado.
    :type managed_profile_id: int
    :param session: Sesión de base de datos inyectada.
    :type session: sqlmodel.Session
    :param current_user: El usuario autenticado que realiza la solicitud.
    :type current_user: app.models.user_model.User
    :return: Una lista de todas las reglas de bloqueo para el perfil especificado.
    :rtype: List[app.models.blocking_rule_model.BlockingRuleRead]
    :raises HTTPException: Propagada desde el servicio si el perfil no se encuentra (404)
                           o el usuario no está autorizado (403).
    """
    return blocking_rule_service.get_blocking_rules_for_profile_service(
        session=session,
        managed_profile_id=managed_profile_id,
        current_user=current_user,
    )

@router.get(
    "/blocking-rules/{blocking_rule_id}",
    response_model=BlockingRuleRead,
    tags=["Reglas de Bloqueo"],
    summary="Obtener una regla de bloqueo específica por ID"
)
def read_blocking_rule_by_id(
    blocking_rule_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> BlockingRuleRead:
    """
    Obtiene una regla de bloqueo específica por su ID.

    El usuario autenticado debe ser el propietario del perfil gestionado
    asociado a esta regla.

    :param blocking_rule_id: El ID de la regla de bloqueo a obtener.
    :type blocking_rule_id: int
    :param session: Sesión de base de datos inyectada.
    :type session: sqlmodel.Session
    :param current_user: El usuario autenticado que realiza la solicitud.
    :type current_user: app.models.user_model.User
    :return: La regla de bloqueo solicitada.
    :rtype: app.models.blocking_rule_model.BlockingRuleRead
    :raises HTTPException: Propagada desde el servicio si la regla no se encuentra (404)
                           o el usuario no está autorizado (403).
    """
    return blocking_rule_service.get_blocking_rule_by_id_service(
        session=session, blocking_rule_id=blocking_rule_id, current_user=current_user
    )

@router.put(
    "/blocking-rules/{blocking_rule_id}",
    response_model=BlockingRuleRead,
    tags=["Reglas de Bloqueo"],
    summary="Actualizar una regla de bloqueo existente"
)
def update_blocking_rule(
    blocking_rule_id: int,
    blocking_rule_in: BlockingRuleUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> BlockingRuleRead:
    """
    Actualiza una regla de bloqueo existente.

    El usuario autenticado debe ser el propietario del perfil gestionado
    asociado a esta regla.

    :param blocking_rule_id: El ID de la regla de bloqueo a actualizar.
    :type blocking_rule_id: int
    :param blocking_rule_in: Los datos para actualizar la regla.
    :type blocking_rule_in: app.models.blocking_rule_model.BlockingRuleUpdate
    :param session: Sesión de base de datos inyectada.
    :type session: sqlmodel.Session
    :param current_user: El usuario autenticado que realiza la solicitud.
    :type current_user: app.models.user_model.User
    :return: La regla de bloqueo actualizada.
    :rtype: app.models.blocking_rule_model.BlockingRuleRead
    :raises HTTPException: Propagada desde el servicio si la regla no se encuentra (404)
                           o el usuario no está autorizado (403).
    """
    return blocking_rule_service.update_blocking_rule_service(
        session=session,
        blocking_rule_id=blocking_rule_id,
        blocking_rule_in=blocking_rule_in,
        current_user=current_user,
    )

@router.delete(
    "/blocking-rules/{blocking_rule_id}",
    response_model=BlockingRuleRead,
    tags=["Reglas de Bloqueo"],
    summary="Eliminar una regla de bloqueo"
)
def delete_blocking_rule(
    blocking_rule_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> BlockingRuleRead:
    """
    Elimina una regla de bloqueo.

    El usuario autenticado debe ser el propietario del perfil gestionado
    asociado a esta regla.

    :param blocking_rule_id: El ID de la regla de bloqueo a eliminar.
    :type blocking_rule_id: int
    :param session: Sesión de base de datos inyectada.
    :type session: sqlmodel.Session
    :param current_user: El usuario autenticado que realiza la solicitud.
    :type current_user: app.models.user_model.User
    :return: La regla de bloqueo eliminada.
    :rtype: app.models.blocking_rule_model.BlockingRuleRead
    :raises HTTPException: Propagada desde el servicio si la regla no se encuentra (404)
                           o el usuario no está autorizado (403).
    """
    return blocking_rule_service.delete_blocking_rule_service(
        session=session, blocking_rule_id=blocking_rule_id, current_user=current_user
    )