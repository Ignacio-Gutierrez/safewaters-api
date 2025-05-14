from pydantic import BaseModel
from typing import List, Optional

class TaskInfo(BaseModel):
    """
    Modelo para la información de la tarea dentro de una respuesta de URLScan.io.

    :ivar url: La URL que fue escaneada.
    :vartype url: Optional[str]
    :ivar domain: El dominio de la URL escaneada.
    :vartype domain: Optional[str]
    :ivar uuid: El identificador único universal (UUID) de la tarea de escaneo.
    :vartype uuid: Optional[str]
    :ivar source: La fuente de la solicitud de escaneo.
    :vartype source: Optional[str]
    :ivar tags: Una lista de etiquetas asociadas con el escaneo (ej. "phishing").
    :vartype tags: Optional[list[str]]
    """
    url: Optional[str] = None
    domain: Optional[str] = None
    uuid: Optional[str] = None
    source: Optional[str] = None
    tags: Optional[list[str]] = None

class PageInfo(BaseModel):
    """
    Modelo para la información de la página dentro de una respuesta de URLScan.io.

    :ivar domain: El dominio principal de la página escaneada.
    :vartype domain: Optional[str]
    """
    domain: Optional[str] = None

class ResultItem(BaseModel):
    """
    Modelo para un ítem de resultado individual en la respuesta de URLScan.io.

    Contiene información sobre la tarea de escaneo y la página resultante.

    :ivar task: Información detallada sobre la tarea de escaneo.
    :vartype task: TaskInfo
    :ivar page: Información sobre la página escaneada.
    :vartype page: Optional[PageInfo]
    """
    task: TaskInfo
    page: Optional[PageInfo] = None

class URLScanioResponse(BaseModel):
    """
    Modelo para la respuesta completa de la API de búsqueda de URLScan.io.

    :ivar results: Una lista de ítems de resultado, cada uno correspondiente a un escaneo.
    :vartype results: List[ResultItem]
    """
    results: List[ResultItem]