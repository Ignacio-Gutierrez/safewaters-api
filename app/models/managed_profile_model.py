import re
import uuid
from typing import Optional, List, TYPE_CHECKING
from beanie import Document, Indexed, Link
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from app.models.user_model import User

class ManagedProfile(Document):
    """Modelo de perfil gestionado por un usuario."""
    name: str
    token: Indexed(str, unique=True)
    manager_user: Link[User]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    url_checking_enabled: bool = Field(default=True, description="Si está habilitada la verificación de URLs para este perfil")
    
    class Settings:
        collection = "managed_profiles"
        indexes = [
            [("manager_user", 1)],
            [("manager_user", 1), ("created_at", -1)],
            [("name", 1), ("manager_user", 1)]  
        ]
    
    @staticmethod
    def slugify(text: str) -> str:
        """Convierte un texto a formato slug (URL-friendly)."""
        text = re.sub(r'[^\w\s-]', '', text.lower())
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')
    
    @staticmethod
    def generate_token(username: str, profile_name: str) -> str:
        """Genera un token único para el perfil."""
        slugified_name = ManagedProfile.slugify(profile_name)
        unique_id = str(uuid.uuid4())[:8]
        return f"{username}-{slugified_name}-{unique_id}"

class ManagedProfileBase(BaseModel):
    """Esquema base para perfil gestionado."""
    name: str

class ManagedProfileCreate(ManagedProfileBase):
    """Esquema para crear un nuevo perfil gestionado."""
    url_checking_enabled: bool = Field(default=True, description="Si está habilitada la verificación de URLs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Perfil Administrado X",
                "url_checking_enabled": True
            }
        }

class ManagedProfileRead(ManagedProfileBase):
    """Esquema para leer datos de un perfil gestionado."""
    id: str = Field(alias="_id")
    token: str
    created_at: datetime
    url_checking_enabled: bool
    
    class Config:
        populate_by_name = True

if TYPE_CHECKING:
    from app.models.user_model import UserRead

class ManagedProfileReadWithManager(ManagedProfileRead):
    """Esquema para leer perfil con información del manager."""
    manager_user: "UserRead"

class ManagedProfileReadWithStats(ManagedProfileRead):
    """Esquema para leer perfil con estadísticas adicionales."""
    manager_user_id: str
    blocking_rules_count: int = 0
    
    class Config:
        populate_by_name = True

class ManagedProfileUpdate(BaseModel):
    """Esquema para actualizar un perfil gestionado."""
    url_checking_enabled: Optional[bool] = None