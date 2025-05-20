"""
Módulo principal del router de la API.

Este módulo agrega y organiza todos los routers de los diferentes endpoints
de la aplicación. Cada sub-módulo en `app.api.endpoints` define sus propias
rutas, y este router principal las incluye bajo un prefijo común si es necesario.
"""
from fastapi import APIRouter

from .endpoints.urls_check import router as urls_check_router
from .endpoints.auth import router as auth_router

api_router = APIRouter()
"""
Router principal de la API.

Instancia de :class:`fastapi.APIRouter` que agrupa todos los routers
específicos de los endpoints.
"""

api_router.include_router(urls_check_router)
"""
Inclusión del router para la verificación de URLs.

Las rutas definidas en :data:`.endpoints.urls_check.router` se añaden
directamente al :data:`api_router`.
"""
api_router.include_router(auth_router, prefix="/auth")
"""
Inclusión del router para la autenticación.

Las rutas definidas en :data:`.endpoints.auth.router` se añaden
al :data:`api_router` bajo el prefijo ``/auth``.
"""