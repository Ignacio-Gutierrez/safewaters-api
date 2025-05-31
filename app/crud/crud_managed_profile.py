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

managed_profile_crud = CRUDManagedProfile()