import math
from typing import List
from beanie import PydanticObjectId
from app.crud.crud_navigation_history import navigation_history_crud
from app.models.navigation_history_model import NavigationHistory, NavigationHistoryResponse
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
                profile_ref_id = None
                try:
                    if record.profile:
                        profile_ref_id = str(record.profile.to_ref().id)
                except Exception:
                    profile_ref_id = str(profile_object_id)
                
                blocking_rule_id = None
                try:
                    if record.blocking_rule:
                        blocking_rule_id = str(record.blocking_rule.to_ref().id)
                except Exception:
                    blocking_rule_id = None
                
                response_item = NavigationHistoryResponse(
                    id=str(record.id),
                    visited_url=record.visited_url,
                    blocked=record.blocked,
                    manaded_profile_id=profile_ref_id or str(profile_object_id),
                    visited_at=record.visited_at.isoformat(),
                    blocking_rule_id=blocking_rule_id
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
    
    async def record_navigation(
        self, 
        profile_id: str, 
        visited_url: str, 
        current_user: User
    ) -> dict:
        """
        Registra una navegación para un perfil específico.
        Retorna información sobre si fue bloqueada o no.
        """
        try:
            navigation = await navigation_history_crud.create_from_profile_id(
                profile_id, 
                visited_url, 
                current_user.id
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
            raise Exception(f"Error al registrar la navegación: {str(e)}")

navigation_history_service = NavigationHistoryService()