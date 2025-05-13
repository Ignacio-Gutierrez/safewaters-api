from fastapi import FastAPI
from app.api.urls import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SafeWaters API",
    description="API para detección de amenazas basada en consultas a servicios externos",
    version="1.0.0"
)

origins = [
    "*" # Permite todos los orígenes (para desarrollo)
    # "chrome-extension://<ID_DE_TU_EXTENSION>",
    # "moz-extension://<ID_DE_TU_EXTENSION>"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"], # Permite todas las cabeceras
)

app.include_router(router)