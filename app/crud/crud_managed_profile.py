from sqlmodel import Session, select
from sqlalchemy.orm import selectinload # Asegúrate de importar selectinload
from typing import List, Optional

from app.models.managed_profile_model import ManagedProfile, ManagedProfileUpdate

def create_managed_profile_db(session: Session, profile_to_create: ManagedProfile) -> ManagedProfile:
    """
    Crea un nuevo perfil gestionado en la base de datos.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param profile_to_create: La instancia del modelo ManagedProfile con los datos a crear.
    :type profile_to_create: app.models.managed_profile_model.ManagedProfile
    :return: El objeto ManagedProfile creado y refrescado desde la base de datos.
    :rtype: app.models.managed_profile_model.ManagedProfile
    """
    session.add(profile_to_create)
    session.commit()
    session.refresh(profile_to_create)
    return profile_to_create

def get_managed_profile_by_id(session: Session, profile_id: int) -> Optional[ManagedProfile]:
    """
    Obtiene un perfil gestionado por su ID.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param profile_id: El ID del perfil gestionado a buscar.
    :type profile_id: int
    :return: El objeto ManagedProfile si se encuentra, de lo contrario None.
    :rtype: Optional[app.models.managed_profile_model.ManagedProfile]
    """
    profile = session.get(ManagedProfile, profile_id)
    return profile

def get_managed_profiles_by_manager_id(session: Session, manager_id: int) -> List[ManagedProfile]:
    """
    Obtiene todos los perfiles gestionados asociados a un ID de manager.
    Carga ansiosamente las reglas de bloqueo para evitar N+1 consultas.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param manager_id: El ID del usuario manager.
    :type manager_id: int
    :return: Una lista de objetos ManagedProfile.
    :rtype: List[app.models.managed_profile_model.ManagedProfile]
    """
    statement = (
        select(ManagedProfile)
        .where(ManagedProfile.manager_user_id == manager_id)
        .options(selectinload(ManagedProfile.blocking_rules))
    )
    profiles = session.exec(statement).all()
    return list(profiles)

def get_managed_profile_by_name_and_manager_id(
    session: Session, profile_name: str, manager_id: int
) -> Optional[ManagedProfile]:
    """
    Obtiene un perfil gestionado por su nombre y el ID del manager.
    Útil para verificar la unicidad del nombre del perfil por manager.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param profile_name: El nombre del perfil a buscar.
    :type profile_name: str
    :param manager_id: El ID del usuario manager.
    :type manager_id: int
    :return: El objeto ManagedProfile si se encuentra, de lo contrario None.
    :rtype: Optional[app.models.managed_profile_model.ManagedProfile]
    """
    statement = select(ManagedProfile).where(
        ManagedProfile.profile_name == profile_name,
        ManagedProfile.manager_user_id == manager_id
    )
    profile = session.exec(statement).first()
    return profile

def get_managed_profile_by_link_code(session: Session, link_code: str) -> Optional[ManagedProfile]:
    """
    Obtiene un perfil gestionado por su código de enlace.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param link_code: El código de enlace del perfil.
    :type link_code: str
    :return: El objeto ManagedProfile si se encuentra, de lo contrario None.
    :rtype: Optional[app.models.managed_profile_model.ManagedProfile]
    """
    statement = select(ManagedProfile).where(ManagedProfile.link_code == link_code)
    profile = session.exec(statement).first()
    return profile


def update_managed_profile_db(
    session: Session,
    db_profile: ManagedProfile,
    profile_update_data: ManagedProfileUpdate
) -> ManagedProfile:
    """
    Actualiza un perfil gestionado existente en la base de datos.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param db_profile: El objeto ManagedProfile existente a actualizar.
    :type db_profile: app.models.managed_profile_model.ManagedProfile
    :param profile_update_data: Un objeto ManagedProfileUpdate con los campos a actualizar.
    :type profile_update_data: app.models.managed_profile_model.ManagedProfileUpdate
    :return: El objeto ManagedProfile actualizado.
    :rtype: app.models.managed_profile_model.ManagedProfile
    """
    update_data = profile_update_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_profile, key, value)
    
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return db_profile

def delete_managed_profile_db(session: Session, profile_id: int) -> Optional[ManagedProfile]:
    """
    Elimina un perfil gestionado de la base de datos por su ID.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param profile_id: El ID del perfil gestionado a eliminar.
    :type profile_id: int
    :return: El objeto ManagedProfile eliminado si se encontró y eliminó, de lo contrario None.
    :rtype: Optional[app.models.managed_profile_model.ManagedProfile]
    """
    profile_to_delete = session.get(ManagedProfile, profile_id)
    if profile_to_delete:
        session.delete(profile_to_delete)
        session.commit()
        return profile_to_delete
    return None


def get_managed_profile_by_link_code(session: Session, link_code: str) -> Optional[ManagedProfile]:
    """
    Obtiene un perfil gestionado por su código de enlace.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param link_code: El código de enlace del perfil.
    :type link_code: str
    :return: El objeto ManagedProfile si se encuentra, de lo contrario None.
    :rtype: Optional[app.models.managed_profile_model.ManagedProfile]
    """
    statement = select(ManagedProfile).where(ManagedProfile.link_code == link_code)
    profile = session.exec(statement).first()
    return profile

def get_managed_profile_by_extension_instance_id(session: Session, extension_instance_id: str) -> Optional[ManagedProfile]:
    """
    Obtiene un perfil gestionado por el ID de instancia de la extensión vinculada.

    :param session: La sesión de base de datos.
    :param extension_instance_id: El ID de la instancia de la extensión.
    :return: El objeto ManagedProfile si se encuentra, de lo contrario None.
    """
    statement = select(ManagedProfile).where(ManagedProfile.extension_instance_id == extension_instance_id)
    profile = session.exec(statement).first()
    return profile