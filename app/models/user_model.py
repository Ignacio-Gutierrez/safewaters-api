from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime
from pydantic import EmailStr

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .managed_profile_model import ManagedProfile, ManagedProfileRead


class UserBase(SQLModel):
    email: EmailStr = Field(max_length=100, unique=True, index=True, nullable=False)
    username: str = Field(max_length=50, unique=True, index=True, nullable=False)


class User(UserBase, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    password_hash: str = Field(max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    managed_profiles: List["ManagedProfile"] = Relationship(back_populates="manager_user")


class UserCreate(UserBase):
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
    id: int
    created_at: datetime


class UserReadWithDetails(UserRead):
    managed_profiles: List["ManagedProfileRead"] = []