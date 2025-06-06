from pydantic import BaseModel, HttpUrl
from typing import Optional

class URLRequest(BaseModel):
    """
    Modelo para la solicitud de verificación y registro de URL.

    Define la estructura esperada para el cuerpo de la solicitud
    cuando se envía una URL para su análisis y registro desde la extensión.

    :ivar url: La URL que se va a verificar. Debe ser una URL HTTP/HTTPS válida.
    :vartype url: pydantic.HttpUrl
    :ivar profile_token: Token del perfil para verificar reglas y registrar navegación.
    :vartype profile_token: str
    """
    url: HttpUrl
    profile_token: str

    class Config:
        """
        Configuración del modelo Pydantic.

        Proporciona un ejemplo de cómo debería ser el JSON de la solicitud.
        """
        json_schema_extra = {
            "example": {
                "url": "https://example.com",
                "profile_token": "user12-perfil-administrado-x-a1b2c3d4",
            }
        }


class URLResponse(BaseModel):
    """
    Modelo para la respuesta de la verificación y registro de URL.

    Define la estructura de la respuesta que se devuelve después de analizar una URL
    y registrarla en el historial de navegación.

    :ivar domain: El dominio extraído de la URL analizada.
    :vartype domain: str
    :ivar malicious: Indica si la URL se considera maliciosa (True) o no (False)
                     según el análisis de fuentes externas.
    :vartype malicious: bool
    :ivar info: Información adicional sobre el resultado de la verificación de fuentes externas.
                 Puede incluir detalles de la fuente de detección o errores.
    :vartype info: str
    :ivar source: La fuente que proporcionó la información sobre la maliciosidad
                  (ej. "Cache", "URLScan.io", "ThreatFox", "AbuseIPDB", "Multi-API").
    :vartype source: str
    :ivar is_blocked_by_user_rule: Indica si la URL está bloqueada por una regla
                                   específica del perfil del usuario (True) o no (False).
    :vartype is_blocked_by_user_rule: bool
    :ivar blocking_rule_details: Detalles de la regla de bloqueo del usuario que se aplicó,
                                 si `is_blocked_by_user_rule` es True.
    :vartype blocking_rule_details: Optional[str]
    """
    domain: str
    malicious: bool
    info: str
    source: str
    is_blocked_by_user_rule: bool = False
    blocking_rule_details: Optional[str] = None

    class Config:
        """
        Configuración del modelo Pydantic.

        Proporciona un ejemplo de cómo debería ser el JSON de la respuesta.
        """
        json_schema_extra = {
            "example": {
                "domain": "example.com",
                "malicious": False,
                "info": "No se detectaron señales de peligro en fuentes consultadas.",
                "source": "Multi-API",
                "is_blocked_by_user_rule": True,
                "blocking_rule_details": "Bloqueado por regla DOMAIN: 'example.com'"
            }
        }