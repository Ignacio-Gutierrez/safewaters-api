from typing import List
from beanie import PydanticObjectId
from app.crud.crud_blocking_rule import blocking_rule_crud
from app.models.blocking_rule_model import (
    BlockingRule, 
    BlockingRuleCreate, 
    BlockingRuleRead,
    BlockingRuleUpdate
)
from app.models.user_model import User

class BlockingRuleService:
    """Servicio para gestionar reglas de bloqueo."""
    
    async def create_rule(
        self, 
        rule_data: BlockingRuleCreate, 
        profile_id: str, 
        current_user: User
    ) -> BlockingRuleRead:
        """Crea una nueva regla de bloqueo."""
        try:
            rule = await blocking_rule_crud.create(rule_data, profile_id, current_user)
            
            return BlockingRuleRead(
                id=str(rule.id),
                rule_type=rule.rule_type,
                rule_value=rule.rule_value,
                active=rule.active,
                description=rule.description,
                created_at=rule.created_at
            )
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al crear la regla: {str(e)}")
    
    async def get_profile_rules(self, profile_id: str, current_user: User) -> List[BlockingRuleRead]:
        """Obtiene todas las reglas de un perfil específico."""
        try:
            profile_object_id = PydanticObjectId(profile_id)
            
            # Verificar que el perfil pertenece al usuario
            from app.crud.crud_managed_profile import managed_profile_crud
            if not await managed_profile_crud.check_ownership(profile_object_id, current_user.id):
                raise ValueError("Perfil no encontrado o no tienes permisos para ver sus reglas")
            
            rules = await blocking_rule_crud.get_by_profile(profile_object_id)
            
            return [
                BlockingRuleRead(
                    id=str(rule.id),
                    rule_type=rule.rule_type,
                    rule_value=rule.rule_value,
                    active=rule.active,
                    description=rule.description,
                    created_at=rule.created_at
                )
                for rule in rules
            ]
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al obtener las reglas: {str(e)}")
    
    async def update_rule(
        self, 
        rule_id: str, 
        update_data: BlockingRuleUpdate, 
        current_user: User
    ) -> BlockingRuleRead:
        """Actualiza una regla de bloqueo."""
        try:
            rule_object_id = PydanticObjectId(rule_id)
            
            # Filtrar solo los campos que no son None
            update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
            
            if not update_dict:
                raise ValueError("No se proporcionaron datos para actualizar")
            
            rule = await blocking_rule_crud.update_by_id_and_user(
                rule_object_id, 
                current_user.id, 
                update_dict
            )
            
            if not rule:
                raise ValueError("Regla no encontrada o no tienes permisos para modificarla")
            
            return BlockingRuleRead(
                id=str(rule.id),
                rule_type=rule.rule_type,
                rule_value=rule.rule_value,
                active=rule.active,
                description=rule.description,
                created_at=rule.created_at
            )
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al actualizar la regla: {str(e)}")
    
    async def delete_rule(self, rule_id: str, current_user: User) -> bool:
        """Elimina una regla de bloqueo."""
        try:
            rule_object_id = PydanticObjectId(rule_id)
            
            deleted = await blocking_rule_crud.delete_by_id_and_user(rule_object_id, current_user.id)
            
            if not deleted:
                raise ValueError("Regla no encontrada o no tienes permisos para eliminarla")
            
            return True
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al eliminar la regla: {str(e)}")

blocking_rule_service = BlockingRuleService()