from pydantic import BaseModel, HttpUrl
from typing import Optional

class URLRequest(BaseModel):
    """
    Modelo para la solicitud de verificación de URL.

    Define la estructura esperada para el cuerpo de la solicitud
    cuando se envía una URL para su análisis.

    :ivar url: La URL que se va a verificar. Debe ser una URL HTTP/HTTPS válida.
    :vartype url: pydantic.HttpUrl
    :ivar extension_instance_id: El ID de instancia de la extensión que realiza la solicitud (opcional).
    :vartype extension_instance_id: Optional[str]
    :ivar page_title: El título de la página que se está visitando (opcional).
    :vartype page_title: Optional[str]
    """
    url: HttpUrl
    extension_instance_id: Optional[str] = None
    page_title: Optional[str] = None

    class Config:
        """
        Configuración del modelo Pydantic.

        Proporciona un ejemplo de cómo debería ser el JSON de la solicitud.
        """
        json_schema_extra = {
            "example": {
                "url": "https://phishing-site.com",
                "extension_instance_id": "unique-extension-id-123",
                "page_title": "Ejemplo de Sitio de Phishing"
            }
        }


class URLResponse(BaseModel):
    """
    Modelo para la respuesta de la verificación de URL.

    Define la estructura de la respuesta que se devuelve después de analizar una URL.

    :ivar domain: El dominio extraído de la URL analizada.
    :vartype domain: str
    :ivar malicious: Indica si la URL se considera maliciosa (True) o no (False).
    :vartype malicious: bool
    :ivar info: Información adicional sobre el resultado de la verificación.
                 Puede incluir detalles de la fuente de detección o errores.
    :vartype info: str
    :ivar source: La fuente que proporcionó la información sobre la maliciosidad
                  (ej. "Cache", "URLScan.io", "ThreatFox", "AbuseIPDB", "Multi-API").
    :vartype source: str
    """
    domain: str
    malicious: bool
    info: str
    source: str

    class Config:
        """
        Configuración del modelo Pydantic.

        Proporciona un ejemplo de cómo debería ser el JSON de la respuesta.
        """
        json_schema_extra = {
            "example": {
                "domain": "phishing-site.com",
                "malicious": True,
                "info": "Listed in 'Api' database",
                "source": "'Api'"
            }
        }
