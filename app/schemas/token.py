from pydantic import BaseModel

class Token(BaseModel):
    """
    Modelo Pydantic para la respuesta del token de acceso.
    Utilizado en el endpoint de login.
    """
    access_token: str
    """El token de acceso JWT."""
    token_type: str
    """El tipo de token (e.g., "bearer")."""

class TokenPayload(BaseModel):
    """
    Modelo Pydantic para el payload contenido dentro de un token JWT.
    Define los campos esperados después de decodificar el token.
    """
    sub: str | None = None
    """
    El "subject" del token, comúnmente el identificador del usuario (e.g., email o ID).
    Es opcional para permitir flexibilidad, aunque generalmente se espera que esté presente.
    """

class TokenValidationRequest(BaseModel):
    """
    Modelo Pydantic para la solicitud de validación de token de perfil.
    Utilizado en el endpoint de validación para extensiones.
    """
    token: str
    """El token del perfil gestionado a validar."""

class TokenValidationResponse(BaseModel):
    """
    Modelo Pydantic para la respuesta de validación de token de perfil.
    Devuelve si el token es válido y la información del perfil asociado.
    """
    valid: bool
    """Indica si el token es válido."""
    profile: dict | None = None
    """Información del perfil asociado si el token es válido, None en caso contrario."""