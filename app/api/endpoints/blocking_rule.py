import logging
import traceback
from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from typing import List, Optional
from app.api.services.blocking_rule_service import blocking_rule_service
from app.models.blocking_rule_model import BlockingRuleCreate, BlockingRuleRead, BlockingRuleUpdate
from app.models.user_model import User
from app.core.security import get_current_user

router = APIRouter()

@router.post("/profile/{profile_id}", response_model=BlockingRuleRead, status_code=status.HTTP_201_CREATED)
async def create_blocking_rule(
    profile_id: str = Path(..., description="ID del perfil al que se asignará la regla"),
    rule_data: BlockingRuleCreate = ...,
    current_user: User = Depends(get_current_user)
) -> BlockingRuleRead:
    """
    Crea una nueva regla de bloqueo para un perfil específico.
    
    - **profile_id**: ID del perfil al que pertenecerá la regla
    - **rule_type**: Tipo de regla (DOMAIN, URL, KEYWORD)
    - **rule_value**: Valor de la regla (dominio, URL o palabra clave)
    - **active**: Si la regla está activa (por defecto True)
    - **description**: Descripción opcional de la regla
    """
    try:
        
        result = await blocking_rule_service.create_rule(rule_data, profile_id, current_user)
        return result
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

@router.get("/profile/{profile_id}", response_model=List[BlockingRuleRead])
async def get_profile_rules(
    profile_id: str = Path(..., description="ID del perfil"),
    current_user: User = Depends(get_current_user)
) -> List[BlockingRuleRead]:
    """
    Obtiene todas las reglas de bloqueo de un perfil específico.
    """
    try:
        return await blocking_rule_service.get_profile_rules(profile_id, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener las reglas"
        )

@router.patch("/{rule_id}", response_model=BlockingRuleRead)
async def update_blocking_rule(
    rule_id: str = Path(..., description="ID de la regla a actualizar"),
    update_data: BlockingRuleUpdate = ...,
    current_user: User = Depends(get_current_user)
) -> BlockingRuleRead:
    """
    Actualiza una regla de bloqueo.
    
    Solo se pueden modificar reglas que pertenecen a perfiles del usuario autenticado.
    """
    try:
        
        result = await blocking_rule_service.update_rule(rule_id, update_data, current_user)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blocking_rule(
    rule_id: str = Path(..., description="ID de la regla a eliminar"),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina una regla de bloqueo.
    
    Solo se pueden eliminar reglas que pertenecen a perfiles del usuario autenticado.
    """
    try:
        await blocking_rule_service.delete_rule(rule_id, current_user)
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