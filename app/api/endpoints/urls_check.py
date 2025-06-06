"""
Módulo de rutas para la API de SafeWaters.

Define los endpoints de la API, incluyendo ``/check`` para la verificación de URLs
y el registro de navegación asociado.
"""
import logging
import traceback
from fastapi import APIRouter, HTTPException, status

from app.schemas.urls_check import URLRequest, URLResponse
from app.api.services.url_check_service import check_and_record_url

router = APIRouter()
"""
Instancia de :class:`fastapi.APIRouter` para registrar las rutas de la API.
"""

@router.post("/check", response_model=URLResponse, tags=["Detección"])
async def check_and_record(request: URLRequest):
    """
    Verifica una URL contra reglas de bloqueo y APIs de seguridad, y registra la navegación.
    
    Endpoint unificado para la extensión del navegador que:
    1. Registra la navegación (siempre se ejecuta)
    2. Verifica reglas de bloqueo del perfil
    3. Si no está bloqueado, verifica APIs de seguridad
    4. Retorna resultado completo con información de navegación
    
    - **url**: URL a verificar
    - **profile_token**: Token del perfil para verificar reglas y registrar navegación
    """
    try:
        result = await check_and_record_url(
            request.profile_token,
            str(request.url)
        )
        
        return URLResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logging.error(f"Error checking and recording URL: {e}")
        logging.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al verificar y registrar la URL"
        )