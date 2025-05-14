"""
Modelos de datos Pydantic para la interacción con la API de AbuseIPDB.

Define las estructuras para los informes de abuso, los datos de una IP
y la respuesta general de la API de AbuseIPDB.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AbuseReport(BaseModel):
    """
    Modelo para un informe individual de abuso de AbuseIPDB.

    :ivar reportedAt: Fecha y hora en que se reportó el abuso.
    :vartype reportedAt: datetime
    :ivar comment: Comentario asociado con el informe (opcional).
    :vartype comment: Optional[str]
    :ivar categories: Lista de IDs de categorías de abuso.
    :vartype categories: List[int]
    :ivar reporterId: ID del reportero.
    :vartype reporterId: int
    :ivar reporterCountryCode: Código del país del reportero (opcional).
    :vartype reporterCountryCode: Optional[str]
    :ivar reporterCountryName: Nombre del país del reportero (opcional).
    :vartype reporterCountryName: Optional[str]
    """
    reportedAt: datetime
    comment: Optional[str] = None
    categories: List[int]
    reporterId: int
    reporterCountryCode: Optional[str] = None
    reporterCountryName: Optional[str] = None

class AbuseIPDBData(BaseModel):
    """
    Modelo para los datos detallados de una dirección IP según AbuseIPDB.

    :ivar ipAddress: La dirección IP que fue consultada.
    :vartype ipAddress: str
    :ivar isPublic: Indica si la IP es pública.
    :vartype isPublic: bool
    :ivar ipVersion: Versión de la IP (4 o 6).
    :vartype ipVersion: int
    :ivar isWhitelisted: Indica si la IP está en lista blanca (opcional).
    :vartype isWhitelisted: Optional[bool]
    :ivar abuseConfidenceScore: Puntuación de confianza de abuso (0-100).
    :vartype abuseConfidenceScore: int
    :ivar countryCode: Código del país de la IP (opcional).
    :vartype countryCode: Optional[str]
    :ivar countryName: Nombre del país de la IP (opcional).
    :vartype countryName: Optional[str]
    :ivar usageType: Tipo de uso de la IP (ej. "Data Center/Web Hosting/Transit") (opcional).
    :vartype usageType: Optional[str]
    :ivar isp: Proveedor de servicios de Internet (ISP) de la IP (opcional).
    :vartype isp: Optional[str]
    :ivar domain: Dominio asociado a la IP (opcional).
    :vartype domain: Optional[str]
    :ivar hostnames: Lista de nombres de host asociados a la IP.
    :vartype hostnames: List[str]
    :ivar isTor: Indica si la IP es un nodo Tor.
    :vartype isTor: bool
    :ivar totalReports: Número total de informes de abuso para esta IP.
    :vartype totalReports: int
    :ivar numDistinctUsers: Número de usuarios distintos que han reportado esta IP.
    :vartype numDistinctUsers: int
    :ivar lastReportedAt: Fecha y hora del último informe de abuso (opcional).
    :vartype lastReportedAt: Optional[datetime]
    :ivar reports: Lista de informes de abuso detallados.
    :vartype reports: List[AbuseReport]
    """
    ipAddress: str
    isPublic: bool
    ipVersion: int
    isWhitelisted: Optional[bool] = None
    abuseConfidenceScore: int
    countryCode: Optional[str] = None
    countryName: Optional[str] = None
    usageType: Optional[str] = None
    isp: Optional[str] = None
    domain: Optional[str] = None
    hostnames: List[str]
    isTor: bool
    totalReports: int
    numDistinctUsers: int
    lastReportedAt: Optional[datetime] = None
    reports: List[AbuseReport] = []

class AbuseIPDBResponse(BaseModel):
    """
    Modelo para la respuesta completa de la API de AbuseIPDB.

    Contiene el objeto de datos principal de la respuesta.

    :ivar data: Objeto que contiene la información detallada de la IP consultada.
    :vartype data: AbuseIPDBData
    """
    data: AbuseIPDBData