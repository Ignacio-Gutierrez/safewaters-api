"""
Módulo principal del router de la API.

Este módulo agrega y organiza todos los routers de los diferentes endpoints
de la aplicación. Cada sub-módulo en :mod:`app.api.endpoints` define sus propias
rutas, y este router principal las incluye bajo un prefijo común si es necesario.
"""
from fastapi import APIRouter

from .endpoints.urls_check import router as urls_check_router
from .endpoints.auth import router as auth_router
from .endpoints.managed_profile import router as profiles_router
from .endpoints.blocking_rule import router as blocking_rules_router
from .endpoints.navigation_history import router as navigation_history_router

api_router = APIRouter()
"""
Router principal de la API.

Instancia de :class:`fastapi.APIRouter` que agrupa todos los routers
específicos de los endpoints de la aplicación.
"""

api_router.include_router(urls_check_router)
"""
Inclusión del router para la verificación de URLs.

Las rutas definidas en :mod:`app.api.endpoints.urls_check.router` se añaden
directamente al :data:`api_router`. Estas rutas gestionan las solicitudes
relacionadas con la comprobación y el análisis de URLs.
"""

api_router.include_router(auth_router, prefix="/auth", tags=["Autenticación"])
"""
Inclusión del router para la autenticación.

Las rutas definidas en :mod:`app.api.endpoints.auth.router` se añaden
al :data:`api_router` bajo el prefijo ``/auth``. Estas rutas manejan
la autenticación de usuarios, el registro y la gestión de tokens.
"""

api_router.include_router(profiles_router, prefix="/managed_profiles", tags=["Perfiles Gestionados"])
"""
Inclusión del router para la gestión de perfiles gestionados.

Las rutas definidas en :mod:`app.api.endpoints.managed_profile.router` se añaden
al :data:`api_router` bajo el prefijo ``/managed_profiles``. Estas rutas permiten
las operaciones CRUD para perfiles gestionados y su vinculación con extensiones.
"""

api_router.include_router(blocking_rules_router, prefix="/rules", tags=["Reglas de Bloqueo"])
"""
Inclusión del router para las reglas de bloqueo.

Las rutas definidas en :mod:`app.api.endpoints.blocking_rule.router` se añaden
al :data:`api_router` bajo el prefijo ``/rules``. Estas rutas permiten
la creación, obtención y gestión de reglas de bloqueo asociadas a perfiles gestionados.
"""

api_router.include_router(navigation_history_router, prefix="/navigation-history", tags=["Historial de Navegación"])
"""
Inclusión del router para el historial de navegación.

Las rutas definidas en :mod:`app.api.endpoints.navigation_history.router` se añaden
al :data:`api_router` bajo el prefijo ``/navigation_history``. Estas rutas permiten
las operaciones CRUD para el historial de navegación de los perfiles gestionados.
"""