"""
Modelos de datos Pydantic para la interacción con la API de ThreatFox.

Define las estructuras para los Indicadores de Compromiso (IOCs) y las respuestas
de la API de ThreatFox.
"""
from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class MalwareSample(BaseModel):
    """
    Modelo para una muestra de malware asociada a un IOC de ThreatFox.

    :ivar time_stamp: Marca de tiempo de la muestra.
    :vartype time_stamp: str
    :ivar md5_hash: Hash MD5 de la muestra de malware.
    :vartype md5_hash: str
    :ivar sha256_hash: Hash SHA256 de la muestra de malware.
    :vartype sha256_hash: str
    :ivar malware_bazaar: URL a la entrada de la muestra en MalwareBazaar.
    :vartype malware_bazaar: pydantic.HttpUrl
    """
    time_stamp: str
    md5_hash: str
    sha256_hash: str
    malware_bazaar: HttpUrl

class ThreatFoxIOC(BaseModel):
    """
    Modelo para un Indicador de Compromiso (IOC) de ThreatFox.

    Representa un único IOC devuelto por la API de ThreatFox.

    :ivar id: Identificador único del IOC.
    :vartype id: str
    :ivar ioc: El valor del indicador de compromiso (ej. una URL, dominio, IP).
    :vartype ioc: str
    :ivar threat_type: Tipo de amenaza (ej. "botnet_cc").
    :vartype threat_type: str
    :ivar threat_type_desc: Descripción del tipo de amenaza.
    :vartype threat_type_desc: str
    :ivar ioc_type: Tipo de IOC (ej. "url", "domain", "ip:port").
    :vartype ioc_type: str
    :ivar ioc_type_desc: Descripción del tipo de IOC.
    :vartype ioc_type_desc: str
    :ivar malware: Nombre del malware asociado.
    :vartype malware: str
    :ivar malware_printable: Nombre del malware en formato imprimible.
    :vartype malware_printable: str
    :ivar malware_alias: Alias del malware.
    :vartype malware_alias: str
    :ivar malware_malpedia: URL a la entrada del malware en Malpedia (opcional).
    :vartype malware_malpedia: Optional[pydantic.HttpUrl]
    :ivar confidence_level: Nivel de confianza del IOC (0-100).
    :vartype confidence_level: int
    :ivar first_seen: Marca de tiempo de la primera vez que se vio el IOC.
    :vartype first_seen: str
    :ivar last_seen: Marca de tiempo de la última vez que se vio el IOC (opcional).
    :vartype last_seen: Optional[str]
    :ivar reference: Referencia externa para el IOC (opcional).
    :vartype reference: Optional[str]
    :ivar reporter: El reportero del IOC.
    :vartype reporter: str
    :ivar tags: Lista de etiquetas asociadas al IOC (opcional).
    :vartype tags: Optional[List[str]]
    :ivar malware_samples: Lista de muestras de malware asociadas (opcional).
    :vartype malware_samples: Optional[List[MalwareSample]]
    """
    id: str
    ioc: str
    threat_type: str
    threat_type_desc: str
    ioc_type: str
    ioc_type_desc: str
    malware: str
    malware_printable: str
    malware_alias: str
    malware_malpedia: Optional[HttpUrl] = None
    confidence_level: int
    first_seen: str
    last_seen: Optional[str] = None
    reference: Optional[str] = None
    reporter: str
    tags: Optional[List[str]] = None
    malware_samples: Optional[List[MalwareSample]] = []

class ThreatFoxResponse(BaseModel):
    """
    Modelo para la respuesta de la API de ThreatFox.

    :ivar query_status: Estado de la consulta a la API (ej. "ok", "no_result").
    :vartype query_status: str
    :ivar data: Lista de Indicadores de Compromiso (IOCs) devueltos por la consulta.
    :vartype data: List[ThreatFoxIOC]
    """
    query_status: str
    data: List[ThreatFoxIOC]