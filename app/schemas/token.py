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