import math
from beanie import PydanticObjectId
from app.crud.crud_navigation_history import navigation_history_crud
from app.models.navigation_history_model import NavigationHistoryResponse
from app.models.pagination_model import PaginatedResponse
from app.models.user_model import User

class NavigationHistoryService:
    """Servicio para gestionar historial de navegación."""
    
    async def get_profile_history_for_frontend(
        self, 
        profile_id: str, 
        current_user: User,
        page: int = 1,
        page_size: int = 10,
        blocked_only: bool = False
    ) -> PaginatedResponse[NavigationHistoryResponse]:
        """
        Obtiene el historial de navegación en el formato esperado por el frontend.
        Solo permite acceso si el usuario es manager del perfil.
        """
        try:
            profile_object_id = PydanticObjectId(profile_id)
            
            from app.crud.crud_managed_profile import managed_profile_crud
            if not await managed_profile_crud.check_ownership(profile_object_id, current_user.id):
                raise ValueError("Perfil no encontrado o no tienes permisos para ver su historial")
            
            if blocked_only:
                records, total_count = await navigation_history_crud.get_blocked_history_paginated(
                    profile_object_id, page, page_size
                )
            else:
                records, total_count = await navigation_history_crud.get_profile_history_paginated(
                    profile_object_id, page, page_size
                )
            
            items = []
            for record in records:
                # Usar datos desnormalizados del snapshot en lugar de hacer consultas
                profile_id = record.profile_snapshot.id
                profile_name = record.profile_snapshot.name
                user_id = record.user_snapshot.id
                user_email = record.user_snapshot.email
                user_username = record.user_snapshot.username
                
                # Datos de la regla de bloqueo (si hay)
                blocking_rule_id = None
                blocking_rule_name = None
                blocking_rule_type = None
                blocking_rule_value = None
                blocking_rule_description = None
                
                if record.blocking_rule_snapshot:
                    blocking_rule_id = record.blocking_rule_snapshot.id
                    blocking_rule_name = record.blocking_rule_snapshot.name
                    blocking_rule_type = record.blocking_rule_snapshot.rule_type
                    blocking_rule_value = record.blocking_rule_snapshot.rule_value
                    blocking_rule_description = record.blocking_rule_snapshot.description
                
                response_item = NavigationHistoryResponse(
                    id=str(record.id),
                    visited_url=record.visited_url,
                    blocked=record.blocked,
                    visited_at=record.visited_at.isoformat(),
                    profile_id=profile_id,
                    profile_name=profile_name,
                    user_id=user_id,
                    user_email=user_email,
                    user_username=user_username,
                    blocking_rule_id=blocking_rule_id,
                    blocking_rule_name=blocking_rule_name,
                    blocking_rule_type=blocking_rule_type,
                    blocking_rule_value=blocking_rule_value,
                    blocking_rule_description=blocking_rule_description
                )
                
                items.append(response_item)
            
            total_pages = math.ceil(total_count / page_size) if total_count > 0 else 0
            
            return PaginatedResponse[NavigationHistoryResponse](
                total_items=total_count,
                total_pages=total_pages,
                current_page=page,
                page_size=page_size,
                items=items
            )
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al obtener el historial: {str(e)}")
    
    async def record_navigation_by_token(
        self, 
        profile_token: str, 
        visited_url: str
    ) -> dict:
        """
        Registra navegación usando el token del perfil.
        Especialmente diseñado para la extensión del navegador.
        """
        try:
            from app.crud.crud_managed_profile import managed_profile_crud
            
            profile = await managed_profile_crud.get_by_token(profile_token)
            if not profile:
                raise ValueError("Token de perfil no válido")
            
            navigation = await navigation_history_crud.create_from_profile_id_without_user_check(
                str(profile.id), 
                visited_url
            )
            
            return {
                "success": True,
                "blocked": navigation.blocked,
                "visited_url": navigation.visited_url,
                "visited_at": navigation.visited_at.isoformat(),
                "navigation_id": str(navigation.id),
                "message": "URL bloqueada por reglas de filtrado" if navigation.blocked else "Navegación registrada"
            }
            
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error al registrar la navegación por token: {str(e)}")

navigation_history_service = NavigationHistoryService()