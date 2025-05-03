from fastapi import FastAPI
from app.api.urls import router

app = FastAPI(
    title="SafeWaters API",
    description="API para detección de amenazas basada en consultas a servicios externos",
    version="1.0.0"
)

app.include_router(router)