from typing import Optional, TYPE_CHECKING
from beanie import Document, Link
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

# Importaciones directas para evitar problemas circulares
from app.models.managed_profile_model import ManagedProfile

# Solo usar TYPE_CHECKING para schemas que no necesitamos en runtime
if TYPE_CHECKING:
    from .managed_profile_model import ManagedProfileRead
    from .blocking_rule_model import BlockingRule, BlockingRuleRead

class RuleType(str, Enum):
    """Tipos de reglas de bloqueo disponibles."""
    DOMAIN = "DOMAIN"
    URL = "URL"
    KEYWORD = "KEYWORD"

class RuleSnapshot(BaseModel):
    """
    Snapshot de una regla de bloqueo en el momento del bloqueo.
    
    Preserva el contexto histórico de la regla que se aplicó,
    independientemente de cambios posteriores en la regla original.
    """
    id: Optional[str] = None  # ID de la regla original para trazabilidad
    name: Optional[str] = None  # Nombre descriptivo de la regla
    rule_type: RuleType
    rule_value: str
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439013",
                "name": "Bloqueo Redes Sociales",
                "rule_type": "DOMAIN",
                "rule_value": "facebook.com",
                "description": "Bloquea acceso a Facebook durante horario escolar",
                "created_at": "2025-06-04T10:30:00.000Z"
            }
        }

class NavigationHistory(Document):
    """
    Modelo para el historial de navegación de perfiles.
    
    Registra cada visita a una URL por parte de un perfil,
    incluyendo información sobre bloqueos aplicados con snapshot
    de la regla para preservar el contexto histórico.
    """
    profile: Link[ManagedProfile]
    visited_at: datetime = Field(default_factory=datetime.utcnow)
    visited_url: str
    blocked: bool = False
    blocking_rule_snapshot: Optional[RuleSnapshot] = None
    
    class Settings:
        collection = "profile_navigation_history"
        indexes = [
            [("profile", 1), ("visited_at", -1)],
            [("profile", 1), ("blocked", 1)],
        ]

# Schemas para requests del cliente (extensión)
class NavigationRecordRequest(BaseModel):
    """Esquema para registrar navegación desde la extensión."""
    profile_token: str
    visited_url: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "profile_token": "user12-perfil-administrado-x-a1b2c3d4",
                "visited_url": "https://example.com/page"
            }
        }

class NavigationHistoryBase(BaseModel):
    """Esquema base para historial de navegación."""
    visited_url: str
    blocked: bool = False

class NavigationHistoryCreate(NavigationHistoryBase):
    """Esquema para crear registro de navegación."""
    pass

class NavigationHistoryRead(NavigationHistoryBase):
    """Esquema para leer historial de navegación."""
    id: str
    visited_at: datetime

# Definir estos esquemas después para evitar problemas de referencia circular
class NavigationHistoryReadWithDetails(NavigationHistoryRead):
    """Esquema con detalles completos."""
    profile: Optional[dict] = None  # Usaremos dict en lugar de ManagedProfileRead
    blocking_rule_snapshot: Optional[RuleSnapshot] = None  # Snapshot en lugar de referencia

class NavigationHistoryResponse(BaseModel):
    """Esquema de respuesta para el frontend."""
    id: str
    visited_url: str
    blocked: bool
    manaded_profile_id: str
    visited_at: str
    blocking_rule_id: Optional[str] = None
    blocking_rule_name: Optional[str] = None
    blocking_rule_description: Optional[str] = None
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "visited_url": "https://example.com/page",
                "blocked": True,
                "manaded_profile_id": "507f1f77bcf86cd799439012", 
                "visited_at": "2025-06-04T10:30:00.000Z",
                "blocking_rule_id": "507f1f77bcf86cd799439013",
                "blocking_rule_name": "Bloqueo Redes Sociales",
                "blocking_rule_description": "Bloquea acceso a Facebook durante horario escolar"
            }
        }