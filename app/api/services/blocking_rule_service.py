"""
Módulo de servicios para gestionar las reglas de bloqueo de perfiles gestionados.

Este módulo proporciona funciones para crear, leer, actualizar y eliminar
reglas de bloqueo, asegurando las comprobaciones de autorización necesarias
basadas en la propiedad del perfil gestionado.
"""
from typing import List, Optional
from sqlmodel import Session
from fastapi import HTTPException, status

from app.crud import crud_blocking_rule
from app.crud import crud_managed_profile
from app.models.blocking_rule_model import (
    BlockingRule,
    BlockingRuleCreate,
    BlockingRuleRead,
    BlockingRuleUpdate,
)
from app.models.user_model import User


def create_blocking_rule_for_profile_service(
    session: Session,
    managed_profile_id: int,
    blocking_rule_in: BlockingRuleCreate,
    current_user: User,
) -> BlockingRuleRead:
    """
    Crea una nueva regla de bloqueo para un perfil gestionado específico.

    Verifica que el `current_user` sea el propietario del perfil gestionado
    antes de crear la regla.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param managed_profile_id: El ID del perfil gestionado para el cual se crea la regla.
    :type managed_profile_id: int
    :param blocking_rule_in: Los datos para la nueva regla de bloqueo.
    :type blocking_rule_in: app.models.blocking_rule_model.BlockingRuleCreate
    :param current_user: El usuario autenticado que realiza la solicitud.
    :type current_user: app.models.user_model.User
    :return: La regla de bloqueo creada.
    :rtype: app.models.blocking_rule_model.BlockingRuleRead
    :raises HTTPException: Si el perfil gestionado no se encuentra (404) o si el usuario
                           no está autorizado para modificar el perfil (403).
    """
    managed_profile = crud_managed_profile.get_managed_profile_by_id(
        session=session, profile_id=managed_profile_id
    )
    if not managed_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Perfil gestionado no encontrado"
        )
    if managed_profile.manager_user_id != current_user.id: # Asumiendo que el campo es manager_user_id
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado para añadir reglas a este perfil gestionado",
        )

    db_blocking_rule = crud_blocking_rule.create_blocking_rule(
        session=session,
        blocking_rule_in=blocking_rule_in,
        managed_profile_id=managed_profile_id,
    )
    return BlockingRuleRead.model_validate(db_blocking_rule)


def get_blocking_rules_for_profile_service(
    session: Session,
    managed_profile_id: int,
    current_user: User,
    skip: int = 0,
    limit: int = 100,
) -> List[BlockingRuleRead]:
    """
    Obtiene todas las reglas de bloqueo para un perfil gestionado específico.

    Verifica que el `current_user` sea el propietario del perfil gestionado.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param managed_profile_id: El ID del perfil gestionado.
    :type managed_profile_id: int
    :param current_user: El usuario autenticado que realiza la solicitud.
    :type current_user: app.models.user_model.User
    :param skip: Número de registros a omitir (para paginación).
    :type skip: int
    :param limit: Número máximo de registros a devolver (para paginación).
    :type limit: int
    :return: Una lista de reglas de bloqueo.
    :rtype: List[app.models.blocking_rule_model.BlockingRuleRead]
    :raises HTTPException: Si el perfil gestionado no se encuentra (404) o si el usuario
                           no está autorizado para acceder al perfil (403).
    """
    managed_profile = crud_managed_profile.get_managed_profile_by_id(
        session=session, profile_id=managed_profile_id
    )
    if not managed_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Perfil gestionado no encontrado"
        )
    if managed_profile.manager_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado para acceder a las reglas de este perfil gestionado",
        )

    rules_db = crud_blocking_rule.get_blocking_rules_by_managed_profile(
        session=session, managed_profile_id=managed_profile_id, skip=skip, limit=limit
    )
    return [BlockingRuleRead.model_validate(rule) for rule in rules_db]


def get_blocking_rule_by_id_service(
    session: Session, blocking_rule_id: int, current_user: User
) -> BlockingRuleRead:
    """
    Obtiene una regla de bloqueo específica por su ID.

    Verifica que el `current_user` sea el propietario del perfil gestionado
    asociado a la regla.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param blocking_rule_id: El ID de la regla de bloqueo a recuperar.
    :type blocking_rule_id: int
    :param current_user: El usuario autenticado que realiza la solicitud.
    :type current_user: app.models.user_model.User
    :return: La regla de bloqueo solicitada.
    :rtype: app.models.blocking_rule_model.BlockingRuleRead
    :raises HTTPException: Si la regla no se encuentra (404) o si el usuario
                           no está autorizado para acceder a la regla (403).
    """
    db_blocking_rule = crud_blocking_rule.get_blocking_rule(
        session=session, blocking_rule_id=blocking_rule_id
    )
    if not db_blocking_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Regla de bloqueo no encontrada"
        )

    managed_profile = crud_managed_profile.get_managed_profile_by_id(
        session=session, profile_id=db_blocking_rule.managed_profile_id
    )
    if not managed_profile or managed_profile.manager_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado para acceder a esta regla de bloqueo",
        )
    return BlockingRuleRead.model_validate(db_blocking_rule)


def update_blocking_rule_service(
    session: Session,
    blocking_rule_id: int,
    blocking_rule_in: BlockingRuleUpdate,
    current_user: User,
) -> BlockingRuleRead:
    """
    Actualiza una regla de bloqueo existente.

    Verifica que el `current_user` sea el propietario del perfil gestionado
    asociado a la regla.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param blocking_rule_id: El ID de la regla de bloqueo a actualizar.
    :type blocking_rule_id: int
    :param blocking_rule_in: Los datos para actualizar la regla de bloqueo.
    :type blocking_rule_in: app.models.blocking_rule_model.BlockingRuleUpdate
    :param current_user: El usuario autenticado que realiza la solicitud.
    :type current_user: app.models.user_model.User
    :return: La regla de bloqueo actualizada.
    :rtype: app.models.blocking_rule_model.BlockingRuleRead
    :raises HTTPException: Si la regla no se encuentra (404) o si el usuario
                           no está autorizado para modificar la regla (403).
    """
    db_blocking_rule = crud_blocking_rule.get_blocking_rule(
        session=session, blocking_rule_id=blocking_rule_id
    )
    if not db_blocking_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Regla de bloqueo no encontrada"
        )

    managed_profile = crud_managed_profile.get_managed_profile_by_id(
        session=session, profile_id=db_blocking_rule.managed_profile_id
    )
    if not managed_profile or managed_profile.manager_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado para modificar esta regla de bloqueo",
        )

    updated_rule = crud_blocking_rule.update_blocking_rule(
        session=session,
        db_blocking_rule=db_blocking_rule,
        blocking_rule_in=blocking_rule_in,
    )
    return BlockingRuleRead.model_validate(updated_rule)


def delete_blocking_rule_service(
    session: Session, blocking_rule_id: int, current_user: User
) -> BlockingRuleRead:
    """
    Elimina una regla de bloqueo.

    Verifica que el `current_user` sea el propietario del perfil gestionado
    asociado a la regla.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param blocking_rule_id: El ID de la regla de bloqueo a eliminar.
    :type blocking_rule_id: int
    :param current_user: El usuario autenticado que realiza la solicitud.
    :type current_user: app.models.user_model.User
    :return: La regla de bloqueo eliminada.
    :rtype: app.models.blocking_rule_model.BlockingRuleRead
    :raises HTTPException: Si la regla no se encuentra (404) o si el usuario
                           no está autorizado para eliminar la regla (403).
    """
    db_blocking_rule = crud_blocking_rule.get_blocking_rule(
        session=session, blocking_rule_id=blocking_rule_id
    )
    if not db_blocking_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Regla de bloqueo no encontrada"
        )

    managed_profile = crud_managed_profile.get_managed_profile_by_id(
        session=session, profile_id=db_blocking_rule.managed_profile_id
    )
    if not managed_profile or managed_profile.manager_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado para eliminar esta regla de bloqueo",
        )

    deleted_rule = crud_blocking_rule.delete_blocking_rule(
        session=session, blocking_rule_id=blocking_rule_id
    )
    if not deleted_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Regla de bloqueo no encontrada para eliminar"
        )
    return BlockingRuleRead.model_validate(deleted_rule)
