"""
Servicio para manejo de tokens de recuperación de contraseña.
"""
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from app.config import settings
from app.models.user_model import User
from app.crud import crud_user
from app.core.security import get_password_hash, is_password_strong_enough
from app.utils.email_service import email_service


class PasswordResetService:
    """Servicio para gestión de recuperación de contraseñas."""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.token_expire_hours = 1  # Token válido por 1 hora
        
        # Almacén temporal de tokens usados (en producción usar Redis)
        self.used_tokens: Dict[str, datetime] = {}
    
    def generate_reset_token(self, user_email: str) -> str:
        """
        Genera un token JWT para recuperación de contraseña.
        
        Args:
            user_email: Email del usuario
            
        Returns:
            str: Token JWT para recuperación
        """
        # Datos del payload
        payload = {
            "sub": user_email,
            "type": "password_reset",
            "exp": datetime.now(timezone.utc) + timedelta(hours=self.token_expire_hours),
            "iat": datetime.now(timezone.utc),
            "jti": secrets.token_urlsafe(16)  # JWT ID único para evitar reutilización
        }
        
        # Generar token
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_reset_token(self, token: str) -> Optional[str]:
        """
        Verifica un token de recuperación y retorna el email del usuario.
        
        Args:
            token: Token de recuperación a verificar
            
        Returns:
            Optional[str]: Email del usuario si el token es válido, None si no
        """
        try:
            # Verificar si el token ya fue usado
            if token in self.used_tokens:
                return None
            
            # Decodificar token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verificar que es un token de recuperación
            if payload.get("type") != "password_reset":
                return None
            
            # Obtener email del usuario
            user_email = payload.get("sub")
            if not user_email:
                return None
            
            return user_email
            
        except ExpiredSignatureError:
            # Token expirado
            return None
        except InvalidTokenError:
            # Token inválido
            return None
        except Exception:
            # Cualquier otro error
            return None
    
    def mark_token_as_used(self, token: str):
        """
        Marca un token como usado para evitar reutilización.
        
        Args:
            token: Token a marcar como usado
        """
        self.used_tokens[token] = datetime.now(timezone.utc)
        
        # Limpiar tokens antiguos (más de 2 horas)
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=2)
        self.used_tokens = {
            t: timestamp for t, timestamp in self.used_tokens.items()
            if timestamp > cutoff_time
        }
    
    async def request_password_reset(self, email: str) -> bool:
        """
        Procesa solicitud de recuperación de contraseña.
        
        Args:
            email: Email del usuario que solicita recuperación
            
        Returns:
            bool: True si se procesó correctamente (siempre retorna True por seguridad)
        """
        try:
            # Buscar usuario por email
            user = await crud_user.get_user_by_email(email)
            
            if user:
                # Generar token de recuperación
                reset_token = self.generate_reset_token(user.email)
                
                # Crear URL de recuperación
                reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
                
                # Enviar correo
                await email_service.send_password_reset_email(
                    to_email=user.email,
                    username=user.username,
                    reset_token=reset_token,
                    reset_url=reset_url
                )
            
            # Siempre retornar True por seguridad (no revelar si el email existe)
            return True
            
        except Exception as e:
            # Log del error pero no exponer detalles
            import logging
            logging.error(f"Error en solicitud de recuperación de contraseña: {e}")
            return True  # Mantener respuesta consistente
    
    async def reset_password(self, token: str, new_password: str) -> tuple[bool, str]:
        """
        Resetea la contraseña usando un token de recuperación.
        
        Args:
            token: Token de recuperación
            new_password: Nueva contraseña
            
        Returns:
            tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Verificar fortaleza de la nueva contraseña
            if not is_password_strong_enough(new_password):
                return False, "La contraseña no cumple con los requisitos de seguridad"
            
            # Verificar token
            user_email = self.verify_reset_token(token)
            if not user_email:
                return False, "Token de recuperación inválido o expirado"
            
            # Buscar usuario
            user = await crud_user.get_user_by_email(user_email)
            if not user:
                return False, "Usuario no encontrado"
            
            # Marcar token como usado
            self.mark_token_as_used(token)
            
            # Actualizar contraseña
            hashed_password = get_password_hash(new_password)
            await crud_user.update_user_password(user.id, hashed_password)
            
            # Enviar notificación de cambio exitoso
            await email_service.send_password_changed_notification(
                to_email=user.email,
                username=user.username
            )
            
            return True, "Contraseña actualizada exitosamente"
            
        except Exception as e:
            import logging
            logging.error(f"Error en reseteo de contraseña: {e}")
            return False, "Error interno del servidor"


# Instancia global del servicio
password_reset_service = PasswordResetService()
