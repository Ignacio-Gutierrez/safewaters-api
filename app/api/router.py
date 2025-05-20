from fastapi import APIRouter

from .endpoints.urls_check import router as urls_check_router

api_router = APIRouter()

api_router.include_router(urls_check_router)