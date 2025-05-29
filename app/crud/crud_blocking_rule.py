from typing import List, Optional

from sqlmodel import Session, select, func  # Asegúrate de que func está importado

from app.models.blocking_rule_model import BlockingRule, BlockingRuleCreate, BlockingRuleUpdate


def create_blocking_rule(
    session: Session, 
    blocking_rule_in: BlockingRuleCreate,
    managed_profile_id: int
) -> BlockingRule:
    """
    Crea una nueva regla de bloqueo asociada a un perfil gestionado.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param blocking_rule_in: Los datos para la nueva regla de bloqueo.
                             Se espera un objeto compatible con BlockingRuleCreate.
    :type blocking_rule_in: app.models.blocking_rule_model.BlockingRuleCreate
    :param managed_profile_id: El ID del perfil gestionado al que pertenece esta regla.
    :type managed_profile_id: int
    :return: La regla de bloqueo creada y persistida en la base de datos.
    :rtype: app.models.blocking_rule_model.BlockingRule
    """
    db_blocking_rule = BlockingRule.model_validate(
        blocking_rule_in, update={"managed_profile_id": managed_profile_id}
    )
    session.add(db_blocking_rule)
    session.commit()
    session.refresh(db_blocking_rule)
    return db_blocking_rule


def get_blocking_rule(
        session: Session, 
        blocking_rule_id: int
) -> Optional[BlockingRule]:
    """
    Obtiene una regla de bloqueo por su ID.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param blocking_rule_id: El ID de la regla de bloqueo a recuperar.
    :type blocking_rule_id: int
    :return: La regla de bloqueo si se encuentra, de lo contrario None.
    :rtype: Optional[app.models.blocking_rule_model.BlockingRule]
    """
    return session.get(BlockingRule, blocking_rule_id)


def get_blocking_rules_by_managed_profile(
    session: Session, 
    managed_profile_id: int
) -> List[BlockingRule]:
    """
    Obtiene todas las reglas de bloqueo para un perfil gestionado específico.
    Las reglas se devuelven ordenadas por ID (implícitamente por orden de creación).

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param managed_profile_id: El ID del perfil gestionado.
    :type managed_profile_id: int
    :return: Una lista de todas las reglas de bloqueo para el perfil especificado.
             La lista puede estar vacía si no hay reglas.
    :rtype: List[app.models.blocking_rule_model.BlockingRule]
    """
    statement = (
        select(BlockingRule)
        .where(BlockingRule.managed_profile_id == managed_profile_id)
        .order_by(BlockingRule.id)
    )
    results = session.exec(statement)
    blocking_rules = results.all()
    return list(blocking_rules)


def update_blocking_rule(
    session: Session, 
    db_blocking_rule: BlockingRule, 
    blocking_rule_in: BlockingRuleUpdate
) -> BlockingRule:
    """
    Actualiza una regla de bloqueo existente.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param db_blocking_rule: El objeto BlockingRule existente a actualizar.
    :type db_blocking_rule: app.models.blocking_rule_model.BlockingRule
    :param blocking_rule_in: Un objeto BlockingRuleUpdate con los campos a actualizar.
    :type blocking_rule_in: app.models.blocking_rule_model.BlockingRuleUpdate
    :return: El objeto BlockingRule actualizado.
    :rtype: app.models.blocking_rule_model.BlockingRule
    """
    if blocking_rule_in.is_active is not None:
        db_blocking_rule.is_active = blocking_rule_in.is_active
        session.add(db_blocking_rule)
        session.commit()
        session.refresh(db_blocking_rule)
    return db_blocking_rule


def delete_blocking_rule(
    session: Session, 
    blocking_rule_id: int
) -> Optional[BlockingRule]:
    """
    Elimina una regla de bloqueo por su ID.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param blocking_rule_id: El ID de la regla de bloqueo a eliminar.
    :type blocking_rule_id: int
    :return: El objeto BlockingRule eliminado si se encontró y eliminó, de lo contrario None.
    :rtype: Optional[app.models.blocking_rule_model.BlockingRule]
    """
    db_blocking_rule = session.get(BlockingRule, blocking_rule_id)
    if db_blocking_rule:
        session.delete(db_blocking_rule)
        session.commit()
        return db_blocking_rule
    return None


async def count_blocking_rules_for_profile(
    session: Session,
    profile_id: int
) -> int:
    """
    Cuenta el número total de reglas de bloqueo para un perfil gestionado.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param profile_id: El ID del perfil gestionado.
    :type profile_id: int
    :return: El número total de reglas de bloqueo.
    :rtype: int
    """
    statement = (
        select(func.count())
        .select_from(BlockingRule)
        .where(BlockingRule.managed_profile_id == profile_id)
    )
    count_value = session.scalar(statement)
    
    return count_value if count_value is not None else 0

async def get_active_blocking_rules_for_profile(
    session: Session, 
    managed_profile_id: int
) -> List[BlockingRule]:
    """
    Obtiene todas las reglas de bloqueo ACTIVAS para un perfil gestionado específico.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param managed_profile_id: El ID del perfil gestionado.
    :type managed_profile_id: int
    :return: Una lista de reglas de bloqueo activas para el perfil especificado.
             La lista puede estar vacía si no hay reglas activas.
    :rtype: List[app.models.blocking_rule_model.BlockingRule]
    """
    statement = (
        select(BlockingRule)
        .where(BlockingRule.managed_profile_id == managed_profile_id)
        .where(BlockingRule.is_active == True)
        .order_by(BlockingRule.id)
    )
    results = session.exec(statement)
    blocking_rules = results.all()
    return list(blocking_rules)