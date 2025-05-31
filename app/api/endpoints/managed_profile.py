from fastapi import APIRouter, HTTPException, Depends, status, Path
from typing import List
from app.api.services.managed_profile_service import managed_profile_service
from app.models.managed_profile_model import ManagedProfileCreate, ManagedProfileRead
from app.models.user_model import User
from app.core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=ManagedProfileRead, status_code=status.HTTP_201_CREATED)
async def create_managed_profile(
    profile_data: ManagedProfileCreate,
    current_user: User = Depends(get_current_user)
) -> ManagedProfileRead:
    """
    Crea un nuevo perfil gestionado.
    
    - **name**: Nombre del perfil (debe ser único por usuario)
    """
    try:
        return await managed_profile_service.create_profile(profile_data, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/", response_model=List[ManagedProfileRead])
async def get_my_profiles(
    current_user: User = Depends(get_current_user)
) -> List[ManagedProfileRead]:
    """
    Obtiene todos los perfiles gestionados del usuario actual.
    """
    try:
        return await managed_profile_service.get_user_profiles(current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener los perfiles"
        )

@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_managed_profile(
    profile_id: str = Path(..., description="ID del perfil a eliminar"),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina un perfil gestionado.
    
    Solo se pueden eliminar perfiles que pertenecen al usuario autenticado.
    
    - **profile_id**: ID del perfil a eliminar
    """
    try:
        await managed_profile_service.delete_profile(profile_id, current_user)
        return
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )