"""
Modelos de datos Pydantic para la interacción con la API de ThreatFox.

Define las estructuras para los Indicadores de Compromiso (IOCs) y las respuestas
de la API de ThreatFox basándose en los campos realmente utilizados.
"""
from pydantic import BaseModel
from typing import List, Optional

class ThreatFoxIOC(BaseModel):
    """
    Modelo simplificado para un Indicador de Compromiso (IOC) de ThreatFox.

    Solo incluye los campos que realmente se utilizan en la implementación actual.

    :ivar id: Identificador único del IOC (opcional).
    :vartype id: Optional[str]
    :ivar ioc: El valor del indicador de compromiso (ej. una URL, dominio, IP).
    :vartype ioc: str
    :ivar confidence_level: Nivel de confianza del IOC (0-100).
    :vartype confidence_level: int
    :ivar threat_type: Tipo de amenaza (ej. "botnet_cc") (opcional).
    :vartype threat_type: Optional[str]
    :ivar malware_printable: Nombre del malware en formato imprimible (opcional).
    :vartype malware_printable: Optional[str]
    :ivar first_seen: Marca de tiempo de la primera vez que se vio el IOC (opcional).
    :vartype first_seen: Optional[str]
    :ivar last_seen: Marca de tiempo de la última vez que se vio el IOC (opcional).
    :vartype last_seen: Optional[str]
    """
    id: Optional[str] = None
    ioc: str
    confidence_level: int
    threat_type: Optional[str] = None
    malware_printable: Optional[str] = None
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None

class ThreatFoxResponse(BaseModel):
    """
    Modelo para la respuesta de la API de ThreatFox.

    :ivar query_status: Estado de la consulta a la API (ej. "ok", "no_result").
    :vartype query_status: str
    :ivar data: Lista de Indicadores de Compromiso (IOCs) devueltos por la consulta (opcional).
              Puede ser None cuando query_status != "ok".
    :vartype data: Optional[List[ThreatFoxIOC]]
    """
    query_status: str
    data: Optional[List[ThreatFoxIOC]] = None