from typing import List
from app.crud.crud_managed_profile import managed_profile_crud
from app.models.managed_profile_model import ManagedProfile, ManagedProfileCreate, ManagedProfileRead
from app.models.user_model import User

class ManagedProfileService:
    """Servicio para gestionar perfiles gestionados."""
    
    async def create_profile(self, profile_data: ManagedProfileCreate, current_user: User) -> ManagedProfileRead:
        """Crea un nuevo perfil gestionado."""
        try:
            # Crear el perfil
            profile = await managed_profile_crud.create(profile_data, current_user)
            
            # Convertir a schema de respuesta
            return ManagedProfileRead(
                id=str(profile.id),
                name=profile.name,
                token=profile.token,
                created_at=profile.created_at
            )
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al crear el perfil: {str(e)}")
    
    async def get_user_profiles(self, current_user: User) -> List[ManagedProfileRead]:
        """Obtiene todos los perfiles de un usuario."""
        profiles = await managed_profile_crud.get_by_user(current_user.id)
        return [
            ManagedProfileRead(
                id=str(profile.id),
                name=profile.name,
                token=profile.token,
                created_at=profile.created_at
            )
            for profile in profiles
        ]

managed_profile_service = ManagedProfileService()