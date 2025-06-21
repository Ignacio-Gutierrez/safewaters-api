from typing import List
from beanie import PydanticObjectId
from app.crud.crud_managed_profile import managed_profile_crud
from app.models.managed_profile_model import ManagedProfile, ManagedProfileCreate, ManagedProfileRead, ManagedProfileReadWithStats, ManagedProfileUpdate
from app.models.user_model import User

class ManagedProfileService:
    """Servicio para gestionar perfiles gestionados."""
    
    async def create_profile(self, profile_data: ManagedProfileCreate, current_user: User) -> ManagedProfileRead:
        """Crea un nuevo perfil gestionado."""
        try:
            profile = await managed_profile_crud.create(profile_data, current_user)
            
            return ManagedProfileRead(
                id=str(profile.id),
                name=profile.name,
                token=profile.token,
                created_at=profile.created_at,
                url_checking_enabled=profile.url_checking_enabled
            )
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al crear el perfil: {str(e)}")
    
    async def get_user_profiles(self, current_user: User) -> List[ManagedProfileReadWithStats]:
        """Obtiene todos los perfiles de un usuario con estadísticas."""
        try:
            profiles_data = await managed_profile_crud.get_by_user_with_stats(current_user.id)
            
            return [
                ManagedProfileReadWithStats(
                    id=str(profile["_id"]),
                    name=profile["name"],
                    token=profile["token"],
                    created_at=profile["created_at"],
                    url_checking_enabled=profile.get("url_checking_enabled", True),
                    manager_user_id=str(profile["manager_user"]["$id"]) if isinstance(profile["manager_user"], dict) else str(profile["manager_user"]),
                    blocking_rules_count=profile.get("blocking_rules_count", 0)
                )
                for profile in profiles_data
            ]
            
        except Exception as e:
            raise Exception(f"Error al obtener los perfiles: {str(e)}")
    
    async def update_profile(self, profile_id: str, profile_update: ManagedProfileUpdate, current_user: User) -> ManagedProfileRead:
        """Actualiza un perfil gestionado."""
        try:
            # Convertir string ID a PydanticObjectId
            profile_object_id = PydanticObjectId(profile_id)
            
            # Verificar que el perfil existe y pertenece al usuario
            if not await managed_profile_crud.check_ownership(profile_object_id, current_user.id):
                raise ValueError("Perfil no encontrado o no tienes permisos para actualizarlo")
            
            # Actualizar el perfil
            updated_profile = await managed_profile_crud.update(profile_object_id, profile_update, current_user.id)
            
            if not updated_profile:
                raise ValueError("Error al actualizar el perfil")
            
            return ManagedProfileRead(
                id=str(updated_profile.id),
                name=updated_profile.name,
                token=updated_profile.token,
                created_at=updated_profile.created_at,
                url_checking_enabled=updated_profile.url_checking_enabled
            )
            
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al actualizar el perfil: {str(e)}")
    
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
            
            # Eliminar el perfil (incluye validación de reglas)
            deleted = await managed_profile_crud.delete_by_id_and_user(profile_object_id, current_user.id)
            
            if not deleted:
                raise Exception("Error al eliminar el perfil")
            
            return True
            
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al eliminar el perfil: {str(e)}")

managed_profile_service = ManagedProfileService()