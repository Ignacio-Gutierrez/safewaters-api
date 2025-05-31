from typing import List, Optional
from beanie import PydanticObjectId
from app.models.managed_profile_model import ManagedProfile, ManagedProfileCreate
from app.models.user_model import User

class CRUDManagedProfile:
    """CRUD operations para ManagedProfile."""
    
    async def create(self, profile_data: ManagedProfileCreate, manager_user: User) -> ManagedProfile:
        """Crea un nuevo perfil gestionado."""
        # Verificar que el usuario no tenga ya un perfil con el mismo nombre
        existing_profile = await self.get_by_name_and_user(profile_data.name, manager_user.id)
        if existing_profile:
            raise ValueError(f"Ya existe un perfil con el nombre '{profile_data.name}' para este usuario")
        
        # Generar token único
        token = ManagedProfile.generate_token(manager_user.username, profile_data.name)
        
        # Crear el perfil
        profile = ManagedProfile(
            name=profile_data.name,
            token=token,
            manager_user=manager_user
        )
        
        await profile.create()
        return profile
    
    async def get_by_name_and_user(self, name: str, user_id: PydanticObjectId) -> Optional[ManagedProfile]:
        """Busca un perfil por nombre y usuario."""
        return await ManagedProfile.find_one(
            ManagedProfile.name == name,
            ManagedProfile.manager_user.id == user_id
        )
    
    async def get_by_token(self, token: str) -> Optional[ManagedProfile]:
        """Busca un perfil por token."""
        return await ManagedProfile.find_one(ManagedProfile.token == token)
    
    async def get_by_user(self, user_id: PydanticObjectId) -> List[ManagedProfile]:
        """Obtiene todos los perfiles de un usuario."""
        return await ManagedProfile.find(ManagedProfile.manager_user.id == user_id).to_list()
    
    async def get_by_id(self, profile_id: PydanticObjectId) -> Optional[ManagedProfile]:
        """Busca un perfil por ID."""
        return await ManagedProfile.get(profile_id)
    
    async def delete_by_id_and_user(self, profile_id: PydanticObjectId, user_id: PydanticObjectId) -> bool:
        """
        Elimina un perfil por ID solo si pertenece al usuario especificado.
        Retorna True si se eliminó correctamente, False si no se encontró.
        """
        profile = await ManagedProfile.find_one(
            ManagedProfile.id == profile_id,
            ManagedProfile.manager_user.id == user_id
        )
        
        if not profile:
            return False
        
        await profile.delete()
        return True
    
    async def check_ownership(self, profile_id: PydanticObjectId, user_id: PydanticObjectId) -> bool:
        """Verifica si un perfil pertenece a un usuario específico."""
        profile = await ManagedProfile.find_one(
            ManagedProfile.id == profile_id,
            ManagedProfile.manager_user.id == user_id
        )
        return profile is not None

managed_profile_crud = CRUDManagedProfile()