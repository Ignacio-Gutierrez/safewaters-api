from sqlmodel import Session, select
from typing import Optional

from app.models.user_model import User

async def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """
    Obtiene un usuario por su dirección de email.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param email: El email del usuario a buscar.
    :type email: str
    :return: El objeto User si se encuentra, de lo contrario None.
    :rtype: Optional[app.models.user_model.User]
    """
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    return user

async def get_user_by_username(session: Session, username: str) -> Optional[User]:
    """
    Obtiene un usuario por su username.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param username: El username del usuario a buscar.
    :type username: str
    :return: El objeto User si se encuentra, de lo contrario None.
    :rtype: Optional[app.models.user_model.User]
    """
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    return user

async def create_user_db(session: Session, user_to_create: User) -> User:
    """
    Crea un nuevo usuario en la base de datos a partir de una instancia del modelo User.

    Se asume que la instancia `user_to_create` ya tiene la contraseña hasheada
    y está lista para ser insertada.

    :param session: La sesión de base de datos.
    :type session: sqlmodel.Session
    :param user_to_create: La instancia del modelo User con los datos del usuario a crear.
    :type user_to_create: app.models.user_model.User
    :return: El objeto User creado y refrescado desde la base de datos.
    :rtype: app.models.user_model.User
    """
    session.add(user_to_create)
    session.commit()
    session.refresh(user_to_create)
    return user_to_create