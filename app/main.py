"""
Módulo principal de la aplicación FastAPI SafeWaters.

Este módulo inicializa la aplicación FastAPI, configura CORS (Cross-Origin Resource Sharing)
y registra los routers de la API.
"""
from fastapi import FastAPI
from app.api.urls import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SafeWaters API",
    description="API para detección de amenazas basada en consultas a servicios externos",
    version="1.0.0"
)
"""
Instancia principal de la aplicación FastAPI.

:title: SafeWaters API
:description: API para detección de amenazas basada en consultas a servicios externos.
:version: 1.0.0
"""

origins = [
    "*" # Permite todos los orígenes (para desarrollo)
    # "chrome-extension://<ID_DE_TU_EXTENSION>",
    # "moz-extension://<ID_DE_TU_EXTENSION>"
]
"""
Lista de orígenes permitidos para las solicitudes CORS.

Durante el desarrollo, se establece en ``["*"]`` para permitir todas las solicitudes.
En producción, se debe restringir a los orígenes específicos de las extensiones
del navegador o de las aplicaciones cliente que consumirán la API.
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"], # Permite todas las cabeceras
)
"""
Configuración del middleware CORS.

Permite solicitudes de los orígenes especificados en la variable ``origins``,
habilita las credenciales, y permite todos los métodos y cabeceras HTTP.
"""

app.include_router(router)
"""
Inclusión del router principal de la API.

El router definido en :mod:`app.api.urls` se añade a la aplicación para
gestionar las rutas de los endpoints.
"""