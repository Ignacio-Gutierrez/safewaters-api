import logging
from typing import List, Optional
from beanie import PydanticObjectId
from app.models.blocking_rule_model import BlockingRule, BlockingRuleCreate
from app.models.managed_profile_model import ManagedProfile
from app.models.user_model import User

logger = logging.getLogger(__name__)

class CRUDBlockingRule:
    """CRUD operations para BlockingRule."""
    
    async def create(self, rule_data: BlockingRuleCreate, profile_id: str, current_user: User) -> BlockingRule:
        """Crea una nueva regla de bloqueo para un perfil."""
        # Convertir profile_id a PydanticObjectId
        profile_object_id = PydanticObjectId(profile_id)
        
        # Verificar que el perfil existe y pertenece al usuario
        profile = await ManagedProfile.find_one(
            ManagedProfile.id == profile_object_id,
            ManagedProfile.manager_user.id == current_user.id
        )
        
        if not profile:
            raise ValueError("Perfil no encontrado o no tienes permisos para crear reglas en él")
        
        # Verificar que no existe una regla duplicada
        existing_rule = await self.get_by_profile_and_value(
            profile_object_id, 
            rule_data.rule_type, 
            rule_data.rule_value
        )
        
        if existing_rule:
            raise ValueError(f"Ya existe una regla {rule_data.rule_type} con el valor '{rule_data.rule_value}' para este perfil")
        
        # Crear la regla
        rule = BlockingRule(
            profile=profile,
            rule_type=rule_data.rule_type,
            rule_value=rule_data.rule_value,
            active=rule_data.active,
            description=rule_data.description,
            name=rule_data.name
        )
        
        await rule.create()
        return rule
    
    async def get_by_profile_and_value(
        self, 
        profile_id: PydanticObjectId, 
        rule_type: str, 
        rule_value: str
    ) -> Optional[BlockingRule]:
        """Busca una regla por perfil, tipo y valor."""
        return await BlockingRule.find_one(
            BlockingRule.profile.id == profile_id,
            BlockingRule.rule_type == rule_type,
            BlockingRule.rule_value == rule_value
        )
    
    async def get_by_profile(self, profile_id: PydanticObjectId) -> List[BlockingRule]:
        """Obtiene todas las reglas de un perfil."""
        return await BlockingRule.find(BlockingRule.profile.id == profile_id).to_list()
    
    async def get_by_user_profiles(self, user_id: PydanticObjectId) -> List[BlockingRule]:
        """Obtiene todas las reglas de todos los perfiles de un usuario."""
        # Primero obtenemos todos los perfiles del usuario
        user_profiles = await ManagedProfile.find(ManagedProfile.manager_user.id == user_id).to_list()
        profile_ids = [profile.id for profile in user_profiles]
        
        # Luego buscamos todas las reglas de esos perfiles
        if not profile_ids:
            return []
        
        return await BlockingRule.find({"profile.$id": {"$in": profile_ids}}).to_list()
    
    async def delete_by_id_and_user(self, rule_id: PydanticObjectId, user_id: PydanticObjectId) -> bool:
        """Elimina una regla si pertenece a un perfil del usuario."""
        rule = await self.get_by_id_and_user(rule_id, user_id)
        if not rule:
            return False
        
        await rule.delete()
        return True
    
    async def update_by_id_and_user(
        self, 
        rule_id: PydanticObjectId, 
        user_id: PydanticObjectId, 
        update_data: dict
    ) -> Optional[BlockingRule]:
        """Actualiza una regla si pertenece a un perfil del usuario."""
        rule = await self.get_by_id_and_user(rule_id, user_id)
        if not rule:
            return None
        
        for field, value in update_data.items():
            if hasattr(rule, field):
                setattr(rule, field, value)
        
        await rule.save()
        return rule

    async def get_by_id_and_user(self, rule_id: PydanticObjectId, user_id: PydanticObjectId) -> Optional[BlockingRule]:
        """Obtiene una regla por ID si pertenece a un perfil del usuario."""
        try:
            rule = await BlockingRule.get(rule_id)
            if not rule:
                return None
            
            # Verificar que el perfil de la regla pertenece al usuario
            await rule.fetch_link(BlockingRule.profile)
            if rule.profile.manager_user.id != user_id:
                return None
            
            return rule
        except Exception as e:
            logger.error(f"Error getting rule by id and user: {str(e)}")
            return None

blocking_rule_crud = CRUDBlockingRule()