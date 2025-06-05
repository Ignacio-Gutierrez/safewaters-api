from typing import List, Optional, Tuple
from beanie import PydanticObjectId
from app.models.navigation_history_model import NavigationHistory, NavigationHistoryCreate, RuleSnapshot
from app.models.managed_profile_model import ManagedProfile

class CRUDNavigationHistory:
    """CRUD operations para NavigationHistory."""
    
    async def create(self, navigation_data: NavigationHistoryCreate, profile: ManagedProfile) -> NavigationHistory:
        """Crea un nuevo registro de navegación."""
        navigation = NavigationHistory(
            profile=profile,
            visited_url=navigation_data.visited_url,
            blocked=navigation_data.blocked
        )
        
        await navigation.create()
        return navigation
    
    async def get_profile_history_paginated(
        self, 
        profile_id: PydanticObjectId, 
        page: int = 1, 
        page_size: int = 10
    ) -> Tuple[List[NavigationHistory], int]:
        """
        Obtiene el historial paginado de un perfil.
        Retorna (lista_registros, total_count).
        """
        skip = (page - 1) * page_size
        
        records = await NavigationHistory.find(
            NavigationHistory.profile.id == profile_id
        ).sort([("visited_at", -1)]).skip(skip).limit(page_size).to_list()
        
        total_count = await NavigationHistory.find(
            NavigationHistory.profile.id == profile_id
        ).count()
        
        return records, total_count
    
    async def get_blocked_history_paginated(
        self, 
        profile_id: PydanticObjectId, 
        page: int = 1, 
        page_size: int = 10
    ) -> Tuple[List[NavigationHistory], int]:
        """
        Obtiene solo el historial bloqueado paginado de un perfil.
        Retorna (lista_registros, total_count).
        """
        skip = (page - 1) * page_size
        
        records = await NavigationHistory.find(
            NavigationHistory.profile.id == profile_id,
            NavigationHistory.blocked == True
        ).sort([("visited_at", -1)]).skip(skip).limit(page_size).to_list()
        
        total_count = await NavigationHistory.find(
            NavigationHistory.profile.id == profile_id,
            NavigationHistory.blocked == True
        ).count()
        
        return records, total_count
    
    async def get_by_profile(self, profile_id: PydanticObjectId) -> List[NavigationHistory]:
        """Obtiene todo el historial de un perfil (sin paginación)."""
        return await NavigationHistory.find(
            NavigationHistory.profile.id == profile_id
        ).sort([("visited_at", -1)]).to_list()
    
    async def get_by_id(self, navigation_id: PydanticObjectId) -> Optional[NavigationHistory]:
        """Busca un registro de navegación por ID."""
        return await NavigationHistory.get(navigation_id)
    
    async def delete_by_profile(self, profile_id: PydanticObjectId) -> bool:
        """Elimina todo el historial de un perfil."""
        result = await NavigationHistory.find(
            NavigationHistory.profile.id == profile_id
        ).delete()
        
        return result.deleted_count > 0

    def _create_rule_snapshot(self, blocking_rule) -> RuleSnapshot:
        """
        Crea un snapshot de una regla de bloqueo.
        Preserva todos los datos relevantes de la regla en el momento del bloqueo.
        """
        return RuleSnapshot(
            id=str(blocking_rule.id),
            name=blocking_rule.name,
            rule_type=blocking_rule.rule_type,
            rule_value=blocking_rule.rule_value,
            description=blocking_rule.description,
            created_at=blocking_rule.created_at
        )

    async def create_from_profile_id_without_user_check(
        self, 
        profile_id: str, 
        visited_url: str
    ) -> NavigationHistory:
        """
        Crea un registro de navegación usando el ID del perfil SIN verificar usuario.
        Usado especialmente para el endpoint /record-by-token desde extensión del navegador.
        """
        from app.crud.crud_managed_profile import managed_profile_crud
        from app.models.blocking_rule_model import BlockingRule
        from urllib.parse import urlparse
        
        profile_object_id = PydanticObjectId(profile_id)
        profile = await managed_profile_crud.get_by_id(profile_object_id)
        if not profile:
            raise ValueError("Perfil no encontrado")
        
        blocked = False
        blocking_rule_snapshot = None
        
        try:
            rules = await BlockingRule.find(
                BlockingRule.profile.id == profile_object_id,
                BlockingRule.active == True
            ).to_list()
            
            parsed_url = urlparse(visited_url)
            domain = parsed_url.netloc.lower()
            
            for rule in rules:
                rule_value = rule.rule_value.lower()
                
                if rule.rule_type == "DOMAIN" and domain == rule_value:
                    blocked = True
                    blocking_rule_snapshot = self._create_rule_snapshot(rule)
                    break
                elif rule.rule_type == "URL" and visited_url.lower() == rule_value:
                    blocked = True
                    blocking_rule_snapshot = self._create_rule_snapshot(rule)
                    break
                elif rule.rule_type == "KEYWORD" and rule_value in visited_url.lower():
                    blocked = True
                    blocking_rule_snapshot = self._create_rule_snapshot(rule)
                    break
                    
        except Exception as e:
            print(f"Error checking blocking rules: {e}")
            pass
        
        navigation = NavigationHistory(
            profile=profile,
            visited_url=visited_url,
            blocked=blocked,
            blocking_rule_snapshot=blocking_rule_snapshot
        )
        
        await navigation.create()
        return navigation

navigation_history_crud = CRUDNavigationHistory()