from typing import List, Optional
from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class User(Document):
    """Modelo de usuario para autenticación y gestión."""
    username: Indexed(str, unique=True)
    email: Indexed(str, unique=True) 
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "users"

class UserBase(BaseModel):
    """Esquema base para usuario."""
    username: str
    email: EmailStr

class UserCreate(UserBase):
    """Esquema para crear usuario."""
    password: str

    class Config:
        """
        Configuración del modelo Pydantic UserCreate.
        Proporciona un ejemplo para la documentación de la API.
        """
        json_schema_extra = {
            "example": {
                "username": "testuser",
                "email": "user@example.com",
                "password": "aStrongPassword123!",
            }
        }
class UserRead(UserBase):
    """Esquema para leer usuario."""
    id: str
    created_at: datetime
    
    @classmethod
    def from_document(cls, user: "User"):
        """Convierte un documento User a UserRead."""
        return cls(
            id=str(user.id),
            username=user.username,
            email=user.email,
            created_at=user.created_at
        )

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserReadWithDetails(UserRead):
    """Esquema con detalles adicionales."""
    pass