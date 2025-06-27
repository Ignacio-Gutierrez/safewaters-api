"""
Esquemas Pydantic para recuperación de contraseña.
"""
from pydantic import BaseModel, EmailStr, Field


class PasswordResetRequest(BaseModel):
    """Esquema para solicitar recuperación de contraseña."""
    email: EmailStr = Field(description="Email del usuario que solicita recuperación")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@ejemplo.com"
            }
        }


class PasswordResetConfirm(BaseModel):
    """Esquema para confirmar nueva contraseña con token."""
    token: str = Field(description="Token de recuperación recibido por email")
    new_password: str = Field(
        min_length=8, 
        description="Nueva contraseña (mínimo 8 caracteres)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "new_password": "NuevaPassword123!"
            }
        }


class PasswordResetResponse(BaseModel):
    """Respuesta de operaciones de recuperación de contraseña."""
    success: bool = Field(description="Si la operación fue exitosa")
    message: str = Field(description="Mensaje descriptivo del resultado")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Se ha enviado un correo con instrucciones para recuperar tu contraseña"
            }
        }
