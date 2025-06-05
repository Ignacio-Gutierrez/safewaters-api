import logging
import traceback
from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from app.api.services.navigation_history_service import navigation_history_service
from app.models.navigation_history_model import (
    NavigationRecordRequest,
    NavigationHistoryResponse
)
from app.models.pagination_model import PaginatedResponse
from app.models.user_model import User
from app.core.security import get_current_user

router = APIRouter()

@router.get("/profile/{profile_id}", response_model=PaginatedResponse[NavigationHistoryResponse])
async def get_profile_history(
    profile_id: str = Path(..., description="ID del perfil"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Número de elementos por página"),
    blocked_only: bool = Query(False, description="Solo mostrar URLs bloqueadas"),
    current_user: User = Depends(get_current_user)
) -> PaginatedResponse[NavigationHistoryResponse]:
    """
    Obtiene el historial de navegación de un perfil específico con paginación.
    
    Solo se puede acceder al historial de perfiles propios.
    
    - **page**: Número de página (empezando desde 1)
    - **page_size**: Número de elementos por página (máximo 100)
    - **blocked_only**: Si es true, solo muestra URLs que fueron bloqueadas
    """
    try:
        return await navigation_history_service.get_profile_history_for_frontend(
            profile_id, current_user, page, page_size, blocked_only
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logging.error(f"Error getting profile history: {e}")
        logging.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener el historial"
        )

@router.post("/record-by-token", status_code=status.HTTP_201_CREATED)
async def record_navigation_by_token(
    request: NavigationRecordRequest
):
    """
    Registra una nueva navegación usando el token del perfil.
    
    Especialmente diseñado para ser usado por la extensión del navegador.
    
    - **profile_token**: Token del perfil
    - **visited_url**: URL visitada
    """
    try:
        result = await navigation_history_service.record_navigation_by_token(
            request.profile_token,
            request.visited_url
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logging.error(f"Error recording navigation by token: {e}")
        logging.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al registrar la navegación"
        )

