from typing import Optional, TYPE_CHECKING
from beanie import Document, Link
from pydantic import BaseModel, Field
from datetime import datetime

from app.models.managed_profile_model import ManagedProfile

# Importar BlockingRule directamente
from app.models.blocking_rule_model import BlockingRule

if TYPE_CHECKING:
    from .managed_profile_model import ManagedProfileRead
    from .blocking_rule_model import BlockingRuleRead

class NavigationHistory(Document):
    """
    Modelo para el historial de navegación de perfiles.
    
    Registra cada visita a una URL por parte de un perfil,
    incluyendo información sobre bloqueos aplicados.
    """
    profile: Link[ManagedProfile]
    visited_at: datetime = Field(default_factory=datetime.utcnow)
    visited_url: str
    blocked: bool = False
    blocking_rule: Optional[Link[BlockingRule]] = None
    
    class Settings:
        collection = "profile_navigation_history"
        indexes = [
            [("profile", 1), ("visited_at", -1)],
            [("profile", 1), ("blocked", 1)],
        ]

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

class NavigationRecordByIdRequest(BaseModel):
    """Esquema para registrar navegación usando ID de perfil directamente."""
    profile_id: str
    visited_url: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "profile_id": "507f1f77bcf86cd799439011",
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

class NavigationHistoryReadWithDetails(NavigationHistoryRead):
    """Esquema con detalles completos."""
    profile: Optional[dict] = None
    blocking_rule: Optional[dict] = None

class NavigationHistoryResponse(BaseModel):
    """Esquema de respuesta para el frontend."""
    visited_url: str
    blocked: bool
    manaded_profile_id: str
    visited_at: str
    blocking_rule_id: Optional[str] = None
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "visited_url": "https://example.com/page",
                "blocked": False,
                "manaded_profile_id": "507f1f77bcf86cd799439012", 
                "visited_at": "2025-06-04T10:30:00.000Z",
                "blocking_rule_id": "507f1f77bcf86cd799439013"
            }
        }