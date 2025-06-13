from typing import Optional, TYPE_CHECKING
from beanie import Document, Link
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum
from urllib.parse import urlparse

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
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    @field_validator('created_at', mode='before')
    @classmethod
    def validate_created_at(cls, v):
        """Asegura que created_at tenga un valor válido."""
        if v is None:
            return datetime.utcnow()
        return v
    
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

class ProfileSnapshot(BaseModel):
    """Datos del perfil desnormalizados."""
    id: str
    name: str
    profile_token: str

class UserSnapshot(BaseModel):
    """Datos del usuario dueño del perfil."""
    id: str
    email: str
    username: Optional[str] = None

class NavigationHistory(Document):
    """
    Historial de navegación optimizado para tu sistema.
    
    Incluye solo los datos que necesitas, desnormalizados
    para evitar múltiples consultas.
    """
    # Referencia original (mantener para integridad)
    profile: Link[ManagedProfile]
    
    # Datos desnormalizados - lo esencial
    profile_snapshot: ProfileSnapshot
    user_snapshot: UserSnapshot
    
    # Datos de navegación
    visited_at: datetime = Field(default_factory=datetime.utcnow)
    visited_url: str
    
    # Datos de bloqueo (tu lógica actual)
    blocked: bool = False
    blocking_rule_snapshot: Optional[RuleSnapshot] = None
    
    class Settings:
        collection = "profile_navigation_history"
        indexes = [
            [("user_snapshot.id", 1), ("visited_at", -1)],
            [("profile_snapshot.id", 1), ("visited_at", -1)],
            [("blocked", 1), ("visited_at", -1)],
            [("user_snapshot.id", 1), ("blocked", 1), ("visited_at", -1)],
            [("profile_snapshot.id", 1), ("blocked", 1), ("visited_at", -1)],
            [("visited_at", -1)],
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
    """Respuesta optimizada con todos los datos en una consulta."""
    id: str
    visited_url: str
    blocked: bool
    visited_at: str
    
    # Datos del perfil (sin más consultas)
    profile_id: str
    profile_name: str
    
    # Datos del usuario (sin más consultas)
    user_id: str
    user_email: str
    user_username: Optional[str] = None
    
    # Datos de la regla (si hay bloqueo)
    blocking_rule_id: Optional[str] = None
    blocking_rule_name: Optional[str] = None
    blocking_rule_type: Optional[str] = None
    blocking_rule_value: Optional[str] = None
    blocking_rule_description: Optional[str] = None
    
    class Config:
        populate_by_name = True