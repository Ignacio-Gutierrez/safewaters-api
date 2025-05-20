from fastapi import APIRouter

# Importa el router de tu endpoint de verificación de URLs
from .endpoints.urls_check import router as urls_check_router

# Aquí importarás otros routers a medida que los crees
# from .endpoints.auth import router as auth_router
# from .endpoints.users import router as users_router
# ... etc.

api_router = APIRouter()

# Incluye el router de verificación de URLs
api_router.include_router(urls_check_router)

# Incluye otros routers aquí
# api_router.include_router(auth_router, prefix="/auth", tags=["Autenticación"])
# api_router.include_router(users_router, prefix="/users", tags=["Usuarios"])
# ... etc.