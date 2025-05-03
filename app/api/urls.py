from fastapi import APIRouter
from app.models.urls import URLRequest, URLResponse
from app.api.services import check_url

router = APIRouter()

@router.post("/check", response_model=URLResponse, tags=["Detección"])
async def check(request: URLRequest): 
    return await check_url(str(request.url))

