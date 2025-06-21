"""
Módulo de seguridad para la gestión de contraseñas y tokens JWT.

Este módulo proporciona funciones para:
- Verificar y hashear contraseñas utilizando ``passlib``.
- Crear y decodificar tokens de acceso JWT (JSON Web Tokens).
- Validar la fortaleza de las contraseñas.
- Obtener el usuario actual a partir de un token JWT para la autenticación de endpoints.
"""
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional

import re
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from app.config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.schemas.token import TokenPayload 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
"""
Contexto de Passlib para el hashing de contraseñas.

Utiliza el esquema ``bcrypt``. La opción ``deprecated="auto"`` permite
la migración automática de hashes si se cambian los esquemas en el futuro.
"""

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
MIN_PASSWORD_LENGTH = 8

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña en texto plano contra un hash almacenado.

    :param plain_password: La contraseña en texto plano a verificar.
    :type plain_password: str
    :param hashed_password: El hash de la contraseña almacenado.
    :type hashed_password: str
    :return: ``True`` si la contraseña coincide, ``False`` en caso contrario.
    :rtype: bool
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Genera el hash de una contraseña utilizando el contexto de Passlib.

    :param password: La contraseña en texto plano a hashear.
    :type password: str
    :return: El hash de la contraseña.
    :rtype: str
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un nuevo token de acceso JWT.

    El token incluirá la información proporcionada en ``data`` y una fecha de expiración.
    El campo "sub" (subject) en ``data`` es comúnmente usado para el identificador del usuario.

    :param data: Diccionario con los datos a incluir en el payload del token (e.g., ``{"sub": "user_email"}``).
    :type data: dict
    :param expires_delta: Opcional. Un objeto ``timedelta`` para especificar una duración
                          diferente a la predeterminada para la expiración del token.
                          Si es ``None``, se utiliza :data:`ACCESS_TOKEN_EXPIRE_MINUTES`.
    :type expires_delta: Optional[timedelta]
    :return: El token JWT codificado como una cadena.
    :rtype: str
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> TokenPayload:
    """
    Decodifica un token JWT y devuelve su payload.

    :param token: El token JWT codificado a decodificar.
    :type token: str
    :raises ExpiredSignatureError: Si el token ha expirado.
    :raises InvalidTokenError: Si el token es inválido por cualquier otra razón 
                               (firma incorrecta, malformado, etc.), que no sea la expiración.
    :return: El payload (claims) del token decodificado.
    :rtype: dict
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="El token ha expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload_dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenPayload(**payload_dict)
    except ExpiredSignatureError:
        raise token_expired_exception
    except InvalidTokenError:
        raise credentials_exception
    except Exception as e:
        raise InvalidTokenError(f"Payload del token inválido: {e}")

def is_password_strong_enough(password: str) -> bool:
    """
    Verifica si la contraseña cumple con los criterios mínimos de fortaleza.

    Criterios:
    - Al menos :data:`MIN_PASSWORD_LENGTH` caracteres.
    - Al menos una letra mayúscula.
    - Al menos una letra minúscula.
    - Al menos un número.
    - Al menos un carácter especial (opcional, actualmente habilitado).

    :param password: La contraseña a verificar.
    :type password: str
    :return: ``True`` si la contraseña es suficientemente fuerte, ``False`` en caso contrario.
    :rtype: bool
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_]", password):
         return False
    return True

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
"""
Esquema de seguridad OAuth2 con flujo de contraseña.

Se utiliza para que FastAPI maneje automáticamente la extracción del token
de las cabeceras de autorización "Bearer". El ``tokenUrl`` apunta al endpoint
de login donde los clientes pueden obtener un token (e.g., ``/api/auth/login``).
"""

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependencia de FastAPI para obtener el usuario actual a partir de un token JWT.

    Este es un callable que FastAPI puede usar en los parámetros de las operaciones de ruta
    para requerir autenticación y obtener el usuario autenticado.

    :param token: Token JWT extraído de la cabecera de autorización por ``oauth2_scheme``.
    :type token: str
    :raises HTTPException: Con código de estado 401 (UNAUTHORIZED) si el token es inválido,
                           ha expirado, el usuario no se encuentra, o las credenciales no se pueden validar.
    :return: El objeto :class:`app.models.user_model.User` correspondiente al token.
    :rtype: app.models.user_model.User
    """
    from app.crud import crud_user
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        if payload.sub is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError: 
        raise credentials_exception
    
    user = await crud_user.get_user_by_email(email=payload.sub)
    if user is None:
        raise credentials_exception
    return user