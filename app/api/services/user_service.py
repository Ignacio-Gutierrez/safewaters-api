"""
Módulo de servicios para la lógica de negocio relacionada con los usuarios.

Este módulo encapsula la lógica de negocio para operaciones de usuario,
como la creación y autenticación, interactuando con la capa CRUD
y utilizando funciones de seguridad.
"""
from sqlmodel import Session
from typing import Optional

from app.models.user_model import User, UserCreate
from app.core.security import verify_password, get_password_hash
from app.crud import crud_user

async def create_user(session: Session, user_in: UserCreate) -> User:
    """
    Crea un nuevo usuario en el sistema.

    Esta función toma los datos de entrada para un nuevo usuario, hashea la contraseña
    proporcionada y luego utiliza la capa CRUD para persistir el usuario en la
    base de datos.

    :param session: La sesión de base de datos para realizar operaciones.
    :type session: sqlmodel.Session
    :param user_in: Los datos del usuario a crear, validados por :class:`app.models.user_model.UserCreate`.
                    Contiene la contraseña en texto plano.
    :type user_in: app.models.user_model.UserCreate
    :return: El objeto :class:`app.models.user_model.User` recién creado y guardado en la base de datos.
    :rtype: app.models.user_model.User
    """
    hashed_password = get_password_hash(user_in.password)
    
    # Excluye la contraseña en texto plano del diccionario de datos
    user_data_for_db = user_in.model_dump(exclude={"password"})
    
    # Crea una instancia del modelo de tabla User con la contraseña hasheada
    db_user_instance = User(**user_data_for_db, password_hash=hashed_password)
    
    return await crud_user.create_user_db(session=session, user_to_create=db_user_instance)

async def authenticate_user(session: Session, email_or_nickname: str, password: str) -> Optional[User]:
    """
    Autentica a un usuario utilizando su email o nickname y su contraseña.

    Primero intenta encontrar al usuario por email. Si no se encuentra, intenta
    buscarlo por nickname. Si se encuentra un usuario, verifica la contraseña
    proporcionida contra el hash almacenado.

    :param session: La sesión de base de datos para realizar operaciones.
    :type session: sqlmodel.Session
    :param email_or_nickname: El email o nickname del usuario que intenta autenticarse.
    :type email_or_nickname: str
    :param password: La contraseña en texto plano proporcionada por el usuario.
    :type password: str
    :return: El objeto :class:`app.models.user_model.User` si la autenticación es exitosa,
             de lo contrario ``None``.
    :rtype: Optional[app.models.user_model.User]
    """
    user = await crud_user.get_user_by_email(session, email_or_nickname)
    
    if not user:
        user = await crud_user.get_user_by_nickname(session, email_or_nickname)
    
    if not user:
        return None 
    
    if not verify_password(password, user.password_hash):
        return None 
        
    return user