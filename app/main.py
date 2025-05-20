"""
Módulo principal de la aplicación FastAPI SafeWaters.

Este módulo inicializa la aplicación FastAPI, configura CORS (Cross-Origin Resource Sharing),
establece eventos de inicio para la creación de la base de datos y registra los routers de la API.
"""
from fastapi import FastAPI
from app.api.router import api_router
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from sqlmodel import SQLModel
import app.models

app = FastAPI(
    title="SafeWaters API",
    description="API para detección de amenazas y control parental",
    version="0.5.0"
)
"""
Instancia principal de la aplicación FastAPI.

Configurada con un título, descripción y versión para la documentación automática de la API (Swagger UI / ReDoc).

:title: SafeWaters API
:description: API para detección de amenazas y control parental.
:version: 0.5.0
"""

@app.on_event("startup")
def on_startup():
    """
    Función de evento que se ejecuta al iniciar la aplicación FastAPI.

    Se encarga de crear todas las tablas en la base de datos definidas por los modelos SQLModel
    (importados a través de ``app.models``), si estas no existen previamente.
    Utiliza el motor de base de datos :data:`app.database.engine` configurado.
    Imprime un mensaje en la consola indicando el resultado de la operación.
    """
    SQLModel.metadata.create_all(engine)
    print("Base de datos y tablas verificadas/creadas (si no existían).")

origins = [
    "*" # Permite todos los orígenes (para desarrollo)
    # "chrome-extension://<ID_DE_TU_EXTENSION>"
]
"""
Lista de orígenes permitidos para las solicitudes CORS (Cross-Origin Resource Sharing).

Durante el desarrollo, se establece en ``["*"]`` para permitir todas las solicitudes desde cualquier origen.
En un entorno de producción, esta lista debe restringirse a los orígenes específicos
de las extensiones del navegador o de las aplicaciones cliente que consumirán la API
para mejorar la seguridad.
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos los métodos HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"], # Permite todas las cabeceras HTTP en las solicitudes
)
"""
Configuración del middleware CORS (Cross-Origin Resource Sharing).

Este middleware se añade a la aplicación FastAPI para gestionar las políticas CORS.
Permite solicitudes de los orígenes especificados en la variable :data:`origins`,
habilita el envío de credenciales (como cookies o cabeceras de autorización)
desde el cliente, y permite todos los métodos y cabeceras HTTP.
"""

app.include_router(api_router, prefix="/api")
"""
Inclusión del router principal de la API.

El router :data:`app.api.router.api_router`, que agrupa todos los endpoints de la API,
se añade a la aplicación FastAPI. Todas las rutas definidas en ``api_router``
estarán prefijadas con ``/api``. Por ejemplo, una ruta ``/users`` en ``api_router``
será accesible en ``/api/users``.
"""