from fastapi import APIRouter, HTTPException, Depends, status, Path
from typing import List
from app.api.services.managed_profile_service import managed_profile_service
from app.models.managed_profile_model import ManagedProfileCreate, ManagedProfileRead, ManagedProfileReadWithStats, ManagedProfile, ManagedProfileUpdate, ManagedProfileUpdate
from app.models.user_model import User
from app.core.security import get_current_user
from app.schemas.token import TokenValidationRequest, TokenValidationResponse

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

@router.get("/", response_model=List[ManagedProfileReadWithStats])
async def get_my_profiles(
    current_user: User = Depends(get_current_user)
) -> List[ManagedProfileReadWithStats]:
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

@router.patch("/{profile_id}", response_model=ManagedProfileRead)
async def update_managed_profile(
    profile_id: str = Path(..., description="ID del perfil a actualizar"),
    profile_update: ManagedProfileUpdate = ...,
    current_user: User = Depends(get_current_user)
) -> ManagedProfileRead:
    """
    Actualiza un perfil gestionado.
    
    - **profile_id**: ID del perfil a actualizar
    - **name**: Nuevo nombre del perfil (opcional)
    - **url_checking_enabled**: Habilita o deshabilita la verificación de URLs (opcional)
    """
    try:
        return await managed_profile_service.update_profile(profile_id, profile_update, current_user)
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

@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_managed_profile(
    profile_id: str = Path(..., description="ID del perfil a eliminar"),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina un perfil gestionado.
    
    Solo se pueden eliminar perfiles que pertenecen al usuario autenticado.
    No se puede eliminar un perfil que tiene reglas de bloqueo asignadas.
    
    - **profile_id**: ID del perfil a eliminar
    """
    try:
        await managed_profile_service.delete_profile(profile_id, current_user)
        return
    except ValueError as e:
        error_message = str(e)
        if "reglas de bloqueo asignadas" in error_message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_message
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/validate-token", response_model=TokenValidationResponse)
async def validate_token(request: TokenValidationRequest):
    """
    Valida un token de perfil para uso por la extensión.
    
    - **token**: Token del perfil a validar
    
    No requiere autenticación ya que es usado por la extensión del navegador.
    """
    try:
        if not request.token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token is required"
            )
        
        profile = await ManagedProfile.find_one({"token": request.token})
        
        if not profile:
            return TokenValidationResponse(
                valid=False,
                profile=None
            )
        
        return TokenValidationResponse(
            valid=True,
            profile={
                "id": str(profile.id),
                "name": profile.name,
                "token": profile.token
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )