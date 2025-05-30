from typing import List, Optional
from sqlmodel import Session, select, func
from datetime import datetime

from app.models.navigation_history_model import NavigationHistory, NavigationHistoryCreate

async def create_navigation_history_entry(
    session: Session,
    history_entry: NavigationHistoryCreate,
    profile_id: int
) -> NavigationHistory:
    """
    Crea una nueva entrada en el historial de navegación para un perfil gestionado.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param history_entry: Los datos para la nueva entrada de historial.
                          Se espera un objeto compatible con NavigationHistoryCreate.
    :type history_entry: app.models.navigation_history_model.NavigationHistoryCreate
    :param profile_id: El ID del perfil gestionado al que pertenece esta entrada.
    :type profile_id: int
    :return: La entrada de historial de navegación creada y persistida en la base de datos.
    :rtype: app.models.navigation_history_model.NavigationHistory
    """
    db_history = NavigationHistory.model_validate(
        history_entry,
        update={
            "managed_profile_id": profile_id,
            "visited_date": datetime.utcnow()
        }
    )
    session.add(db_history)
    session.commit()
    session.refresh(db_history)
    return db_history

async def count_navigation_history_for_profile(
    session: Session,
    profile_id: int
) -> int:
    """
    Cuenta el número total de entradas de historial de navegación para un perfil gestionado.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param profile_id: El ID del perfil gestionado.
    :type profile_id: int
    :return: El número total de entradas de historial.
    :rtype: int
    """
    statement = (
        select(func.count())
        .select_from(NavigationHistory)
        .where(NavigationHistory.managed_profile_id == profile_id)
    )
    count_value = session.scalar(statement)
    
    return count_value if count_value is not None else 0

async def count_navigation_history_by_blocking_rule_id(
    session: Session,
    blocking_rule_id: int
) -> int:
    """
    Cuenta el número de entradas de historial de navegación asociadas a un ID de regla de bloqueo.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param blocking_rule_id: El ID de la regla de bloqueo.
    :type blocking_rule_id: int
    :return: El número de entradas de historial asociadas.
    :rtype: int
    """
    statement = (
        select(func.count())
        .select_from(NavigationHistory)
        .where(NavigationHistory.blocking_rule_id == blocking_rule_id)
    )
    count_value = session.scalar(statement)
    return count_value if count_value is not None else 0

async def get_navigation_history_for_profile(
    session: Session,
    profile_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[NavigationHistory]:
    """
    Obtiene el historial de navegación para un perfil gestionado específico, con paginación.

    Las entradas se devuelven ordenadas por fecha de visita descendente (la más reciente primero).

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param profile_id: El ID del perfil gestionado.
    :type profile_id: int
    :param skip: Número de registros a saltar (para paginación).
    :type skip: int
    :param limit: Número máximo de registros a devolver (para paginación).
    :type limit: int
    :return: Una lista de entradas de historial de navegación para el perfil especificado.
             La lista puede estar vacía si no hay entradas o si los parámetros de paginación
             exceden el número de registros.
    :rtype: List[app.models.navigation_history_model.NavigationHistory]
    """
    statement = (
        select(NavigationHistory)
        .where(NavigationHistory.managed_profile_id == profile_id)
        .order_by(NavigationHistory.visited_date.desc())
        .offset(skip)
        .limit(limit)
    )
    results = session.exec(statement)
    history_entries = results.all()
    return list(history_entries)