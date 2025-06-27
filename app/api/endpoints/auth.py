"""
Módulo de endpoints para la autenticación y registro de usuarios.

Proporciona rutas para:
- Registrar nuevos usuarios.
- Iniciar sesión y obtener un token de acceso JWT.
- Recuperación de contraseña por correo electrónico.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.models.user_model import UserCreate, UserRead
from app.schemas.token import Token
from app.schemas.password_reset import (
    PasswordResetRequest, 
    PasswordResetConfirm, 
    PasswordResetResponse
)

from app.core.security import (
    create_access_token,
    is_password_strong_enough,
    MIN_PASSWORD_LENGTH
)

from app.crud import crud_user
from app.api.services import user_service
from app.services.password_reset_service import password_reset_service

router = APIRouter()
"""
Router de FastAPI para los endpoints de autenticación y gestión de usuarios.
"""

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_new_user(
    user_in: UserCreate
) -> UserRead:
    """
    Crea un nuevo usuario (manager/admin).

    Verifica si el email o username ya existen en la base de datos.
    Valida la fortaleza de la contraseña.
    Si todas las validaciones son exitosas, crea el usuario a través del servicio de usuarios.

    :param user_in: Datos del usuario a crear, validados por :class:`app.models.user_model.UserCreate`.
    :type user_in: app.models.user_model.UserCreate
    :raises HTTPException 400: Si el email ya existe.
    :raises HTTPException 400: Si el username ya existe.
    :raises HTTPException 400: Si la contraseña no es suficientemente fuerte.
    :return: Los datos del usuario creado, excluyendo la contraseña, según :class:`app.models.user_model.UserRead`.
    :rtype: app.models.user_model.UserRead
    """
    existing_user_by_email = await crud_user.get_user_by_email(email=user_in.email)
    if existing_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este email.",
        )
    
    existing_user_by_username = await crud_user.get_user_by_username(username=user_in.username)
    if existing_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este username.",
        )
    
    if not is_password_strong_enough(user_in.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"La contraseña no es lo suficientemente segura. Debe tener al menos {MIN_PASSWORD_LENGTH} caracteres, "
                "incluir mayúsculas, minúsculas y números."
            ),
        )
    
    created_user = await user_service.create_user(user_in)
    
    return UserRead.from_document(created_user)


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """
    Inicio de sesión compatible con OAuth2 para obtener un token de acceso.

    El campo ``username`` del formulario puede ser el email o el username del usuario.
    Autentica al usuario y, si es exitoso, genera y devuelve un token JWT.

    :param form_data: Datos del formulario OAuth2 (username y password).
                      ``form_data.username`` puede ser email o username.
    :type form_data: fastapi.security.OAuth2PasswordRequestForm
    :raises HTTPException 401: Si el email/username o la contraseña son incorrectos.
    :return: Un objeto :class:`app.schemas.token.Token` conteniendo el ``access_token`` y ``token_type``.
    :rtype: app.schemas.token.Token
    """
    user = await user_service.authenticate_user(
        email_or_username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email/username o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.email} 
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/request-password-reset", response_model=PasswordResetResponse)
async def request_password_reset(request: PasswordResetRequest) -> PasswordResetResponse:
    """
    Solicita recuperación de contraseña por correo electrónico.
    
    Envía un correo con un enlace para restablecer la contraseña.
    Siempre retorna éxito por seguridad (no revela si el email existe).
    
    - **email**: Dirección de correo electrónico del usuario
    """
    try:
        await password_reset_service.request_password_reset(request.email)
        
        return PasswordResetResponse(
            success=True,
            message="Si tu email está registrado, recibirás instrucciones para recuperar tu contraseña"
        )
        
    except Exception as e:
        import logging
        logging.error(f"Error en solicitud de recuperación: {e}")
        
        return PasswordResetResponse(
            success=True,
            message="Si tu email está registrado, recibirás instrucciones para recuperar tu contraseña"
        )


@router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(request: PasswordResetConfirm) -> PasswordResetResponse:
    """
    Restablece la contraseña usando un token de recuperación.
    
    El token se obtiene del correo de recuperación enviado previamente.
    
    - **token**: Token de recuperación recibido por email
    - **new_password**: Nueva contraseña (debe cumplir requisitos de seguridad)
    """
    try:
        success, message = await password_reset_service.reset_password(
            request.token, 
            request.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return PasswordResetResponse(
            success=True,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Error en reseteo de contraseña: {e}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )