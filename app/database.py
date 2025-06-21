"""
Módulo de configuración y gestión de la base de datos MongoDB.

Este módulo se encarga de establecer la conexión con MongoDB
utilizando Motor (async MongoDB driver) y Beanie (ODM).
Proporciona funciones para inicializar la base de datos y configurar
los modelos Document para MongoDB.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
import logging

logger = logging.getLogger(__name__)

MONGODB_URL = settings.MONGODB_URL
"""
URL de conexión a MongoDB.

Se obtiene de la configuración de la aplicación (``settings.MONGODB_URL``).
Ejemplo: ``"mongodb://localhost:27017"`` o ``"mongodb://user:password@host:port/database"``.
"""

DATABASE_NAME = settings.DATABASE_NAME
"""
Nombre de la base de datos MongoDB.

Se obtiene de la configuración de la aplicación (``settings.DATABASE_NAME``).
Ejemplo: ``"safewaters"``.
"""

# Cliente MongoDB global
mongodb_client: AsyncIOMotorClient = None
"""
Cliente global de MongoDB.

Se inicializa durante el startup de la aplicación mediante :func:`init_database`.
"""

async def init_database():
    """
    Inicializa la conexión a MongoDB y configura Beanie ODM.
    
    Esta función reemplaza a create_db_and_tables() del mundo SQLModel.
    Se ejecuta durante el startup de FastAPI para establecer la conexión
    con MongoDB e inicializar todos los modelos Document.
    
    :raises Exception: Si no se puede conectar a MongoDB o inicializar Beanie.
    """
    global mongodb_client
    
    try:
        # Crear cliente MongoDB
        mongodb_client = AsyncIOMotorClient(MONGODB_URL)
        
        # Seleccionar base de datos
        database = mongodb_client[DATABASE_NAME]
        
        # Verificar conexión
        await mongodb_client.admin.command('ping')
        logger.info(f"Conectado exitosamente a MongoDB: {DATABASE_NAME}")
        
        # Importar todos los modelos Document
        from app.models.user_model import User
        from app.models.managed_profile_model import ManagedProfile
        from app.models.blocking_rule_model import BlockingRule
        from app.models.navigation_history_model import NavigationHistory
        
        # Inicializar Beanie con todos los modelos
        await init_beanie(
            database=database,
            document_models=[
                User,
                ManagedProfile, 
                BlockingRule,
                NavigationHistory
            ]
        )
        
        logger.info("Beanie ODM inicializado correctamente con todos los modelos")
        
    except Exception as e:
        logger.error(f"Error al inicializar MongoDB: {str(e)}")
        raise


async def close_database():
    """
    Cierra la conexión a MongoDB.
    
    Función opcional para cerrar limpiamente la conexión durante el shutdown
    de la aplicación FastAPI.
    """
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.info("Conexión a MongoDB cerrada")
