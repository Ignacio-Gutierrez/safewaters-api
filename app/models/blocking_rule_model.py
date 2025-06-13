from typing import Optional, TYPE_CHECKING
from beanie import Document, Link
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

# Importación directa para evitar problemas de referencia circular
from app.models.managed_profile_model import ManagedProfile

class RuleType(str, Enum):
    """Tipos de reglas de bloqueo disponibles."""
    DOMAIN = "DOMAIN"
    URL = "URL"
    KEYWORD = "KEYWORD"

class BlockingRule(Document):
    """
    Modelo para reglas de bloqueo de contenido.
    
    Define reglas específicas que determinan qué contenido
    debe ser bloqueado para un perfil determinado.
    """
    profile: Link[ManagedProfile]
    name: Optional[str] = None
    rule_type: RuleType
    rule_value: str
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    description: Optional[str] = None
    
    class Settings:
        collection = "blocking_rules"
        indexes = [
            [("profile", 1), ("active", 1), ("rule_type", 1)],
            [("profile", 1), ("created_at", -1)]
        ]

# Esquemas Pydantic
class BlockingRuleBase(BaseModel):
    """Esquema base para reglas de bloqueo."""
    name: Optional[str] = None
    rule_type: RuleType
    rule_value: str
    active: bool = True
    description: Optional[str] = None

class BlockingRuleCreate(BlockingRuleBase):
    """Esquema para crear regla de bloqueo."""
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Bloqueo Redes Sociales",
                "rule_type": "KEYWORD",
                "rule_value": "exampl",
                "active": True,
                "description": "Bloquear acceso al dominio example.com"
            }
        }

class BlockingRuleRead(BlockingRuleBase):
    """Esquema para leer regla de bloqueo."""
    id: str
    created_at: datetime

if TYPE_CHECKING:
    from app.models.managed_profile_model import ManagedProfileRead

class BlockingRuleReadWithProfile(BlockingRuleRead):
    """Esquema con información del perfil."""
    profile: "ManagedProfileRead"

class BlockingRuleUpdate(BaseModel):
    """Esquema para actualizar regla de bloqueo."""
    name: Optional[str] = None
    active: Optional[bool] = None
    description: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Nuevo nombre de regla",
                "active": False,
                "description": "Nueva descripción"
            }
        }