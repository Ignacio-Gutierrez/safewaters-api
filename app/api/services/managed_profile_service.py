from typing import List
from beanie import PydanticObjectId
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
    
    async def delete_profile(self, profile_id: str, current_user: User) -> bool:
        """
        Elimina un perfil gestionado.
        Solo permite eliminar perfiles que pertenecen al usuario actual.
        """
        try:
            # Convertir string ID a PydanticObjectId
            profile_object_id = PydanticObjectId(profile_id)
            
            # Verificar que el perfil existe y pertenece al usuario
            if not await managed_profile_crud.check_ownership(profile_object_id, current_user.id):
                raise ValueError("Perfil no encontrado o no tienes permisos para eliminarlo")
            
            # Eliminar el perfil
            deleted = await managed_profile_crud.delete_by_id_and_user(profile_object_id, current_user.id)
            
            if not deleted:
                raise Exception("Error al eliminar el perfil")
            
            return True
            
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al eliminar el perfil: {str(e)}")

managed_profile_service = ManagedProfileService()