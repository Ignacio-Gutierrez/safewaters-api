from typing import List, Optional
from beanie import PydanticObjectId
from app.models.managed_profile_model import ManagedProfile, ManagedProfileCreate, ManagedProfileUpdate
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
            manager_user=manager_user,
            url_checking_enabled=profile_data.url_checking_enabled
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
    
    async def get_by_user_with_stats(self, user_id: PydanticObjectId) -> List[dict]:
        """Obtiene todos los perfiles de un usuario con estadísticas."""
        try:
            profiles = await self.get_by_user(user_id)
            
            result = []
            for profile in profiles:
                try:
                    from app.models.blocking_rule_model import BlockingRule
                    rules_count = await BlockingRule.find(BlockingRule.profile.id == profile.id).count()
                    
                    manager_user_id = None
                    if profile.manager_user:
                        manager_user_id = profile.manager_user.to_ref().id
                    
                    profile_dict = {
                        "_id": profile.id,
                        "name": profile.name,
                        "token": profile.token,
                        "manager_user": {"$id": manager_user_id} if manager_user_id else None,
                        "created_at": profile.created_at,
                        "url_checking_enabled": profile.url_checking_enabled,
                        "blocking_rules_count": rules_count
                    }
                    result.append(profile_dict)
                    
                except Exception as e:
                    manager_user_id = None
                    try:
                        if profile.manager_user:
                            manager_user_id = profile.manager_user.to_ref().id
                    except:
                        pass
                        
                    profile_dict = {
                        "_id": profile.id,
                        "name": profile.name,
                        "token": profile.token,
                        "manager_user": {"$id": manager_user_id} if manager_user_id else None,
                        "created_at": profile.created_at,
                        "url_checking_enabled": profile.url_checking_enabled,
                        "blocking_rules_count": 0
                    }
                    result.append(profile_dict)
            
            result.sort(key=lambda x: x["created_at"], reverse=True)
            return result
            
        except Exception as e:
            raise e
    
    async def get_by_id(self, profile_id: PydanticObjectId) -> Optional[ManagedProfile]:
        """Busca un perfil por ID."""
        return await ManagedProfile.get(profile_id)
    
    async def has_blocking_rules(self, profile_id: PydanticObjectId) -> bool:
        """Verifica si un perfil tiene reglas de bloqueo asignadas."""
        from app.models.blocking_rule_model import BlockingRule
        
        rules_count = await BlockingRule.find(BlockingRule.profile.id == profile_id).count()
        return rules_count > 0
    
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
        
        # Verificar si el perfil tiene reglas asignadas
        if await self.has_blocking_rules(profile_id):
            raise ValueError("No se puede eliminar el perfil porque tiene reglas de bloqueo asignadas")
        
        await profile.delete()
        return True
    
    async def update(self, profile_id: PydanticObjectId, profile_update: ManagedProfileUpdate, user_id: PydanticObjectId) -> Optional[ManagedProfile]:
        """Actualiza un perfil gestionado."""
        profile = await ManagedProfile.find_one(
            ManagedProfile.id == profile_id,
            ManagedProfile.manager_user.id == user_id
        )
        
        if not profile:
            return None
        
        update_data = profile_update.model_dump(exclude_unset=True)
        if update_data:
            for field, value in update_data.items():
                setattr(profile, field, value)
            await profile.save()
        
        return profile
    
    async def check_ownership(self, profile_id: PydanticObjectId, user_id: PydanticObjectId) -> bool:
        """Verifica si un perfil pertenece a un usuario específico."""
        profile = await ManagedProfile.find_one(
            ManagedProfile.id == profile_id,
            ManagedProfile.manager_user.id == user_id
        )
        return profile is not None

managed_profile_crud = CRUDManagedProfile()