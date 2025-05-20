"""
Módulo de endpoints para la autenticación y registro de usuarios.

Proporciona rutas para:
- Registrar nuevos usuarios.
- Iniciar sesión y obtener un token de acceso JWT.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.database import get_session
from app.models.user_model import UserCreate, UserRead
from app.schemas.token import Token

from app.core.security import (
    create_access_token,
    is_password_strong_enough,
    MIN_PASSWORD_LENGTH
)

from app.crud import crud_user
from app.api.services import user_service

router = APIRouter()
"""
Router de FastAPI para los endpoints de autenticación y gestión de usuarios.
"""

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED, tags=["Autenticación y Usuarios"])
async def register_new_user(
    *,
    session: Session = Depends(get_session),
    user_in: UserCreate
) -> UserRead:
    """
    Crea un nuevo usuario (manager/padre).

    Verifica si el email o nickname ya existen en la base de datos.
    Valida la fortaleza de la contraseña.
    Si todas las validaciones son exitosas, crea el usuario a través del servicio de usuarios.

    :param session: Sesión de base de datos inyectada por dependencia.
    :type session: sqlmodel.Session
    :param user_in: Datos del usuario a crear, validados por :class:`app.models.user_model.UserCreate`.
    :type user_in: app.models.user_model.UserCreate
    :raises HTTPException 400: Si el email ya existe.
    :raises HTTPException 400: Si el nickname ya existe.
    :raises HTTPException 400: Si la contraseña no es suficientemente fuerte.
    :return: Los datos del usuario creado, excluyendo la contraseña, según :class:`app.models.user_model.UserRead`.
    :rtype: app.models.user_model.UserRead
    """
    existing_user_by_email = await crud_user.get_user_by_email(session=session, email=user_in.email)
    if existing_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este email.",
        )
    
    existing_user_by_nickname = await crud_user.get_user_by_nickname(session=session, nickname=user_in.nickname)
    if existing_user_by_nickname:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este nickname.",
        )
    
    if not is_password_strong_enough(user_in.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"La contraseña no es lo suficientemente segura. Debe tener al menos {MIN_PASSWORD_LENGTH} caracteres, "
                "incluir mayúsculas, minúsculas y números."
            ),
        )
    
    created_user = await user_service.create_user(session=session, user_in=user_in)
    return created_user


@router.post("/login", response_model=Token, tags=["Autenticación y Usuarios"])
async def login_for_access_token(
    session: Session = Depends(get_session), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """
    Inicio de sesión compatible con OAuth2 para obtener un token de acceso.

    El campo ``username`` del formulario puede ser el email o el nickname del usuario.
    Autentica al usuario y, si es exitoso, genera y devuelve un token JWT.

    :param session: Sesión de base de datos inyectada por dependencia.
    :type session: sqlmodel.Session
    :param form_data: Datos del formulario OAuth2 (username y password).
                      ``form_data.username`` puede ser email o nickname.
    :type form_data: fastapi.security.OAuth2PasswordRequestForm
    :raises HTTPException 401: Si el email/nickname o la contraseña son incorrectos.
    :return: Un objeto :class:`app.schemas.token.Token` conteniendo el ``access_token`` y ``token_type``.
    :rtype: app.schemas.token.Token
    """
    user = await user_service.authenticate_user(
        session=session, email_or_nickname=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email/nickname o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.email} 
    )
    return Token(access_token=access_token, token_type="bearer")