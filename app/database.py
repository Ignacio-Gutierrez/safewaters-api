"""
Módulo de configuración y gestión de la base de datos.

Este módulo se encarga de establecer la conexión con la base de datos
utilizando la URL definida en la configuración de la aplicación.
Proporciona un motor (engine) de SQLAlchemy para interactuar con la base de datos
y funciones para crear las tablas y obtener sesiones de base de datos.
"""
from sqlmodel import create_engine, Session, SQLModel
from app.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
"""
URL de conexión a la base de datos.

Se obtiene de la configuración de la aplicación (``settings.DATABASE_URL``).
Ejemplo: ``"sqlite:///./safewaters.db"`` o ``"postgresql://user:password@host:port/database"``.
"""

connect_args = {}
if SQLALCHEMY_DATABASE_URL and "sqlite" in SQLALCHEMY_DATABASE_URL.lower():
    connect_args = {"check_same_thread": False}
"""
Argumentos de conexión adicionales para el motor de SQLAlchemy.

Para bases de datos SQLite, se establece ``{"check_same_thread": False}``
para permitir que el motor sea utilizado por múltiples hilos, lo cual es
necesario para FastAPI cuando se usa SQLite.
"""

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    echo=True # Imprime las sentencias SQL ejecutadas, útil para depuración.
)
"""
Motor (engine) de SQLAlchemy para la conexión a la base de datos.

Se crea utilizando la :data:`SQLALCHEMY_DATABASE_URL` y los :data:`connect_args`.
La opción ``echo=True`` hace que SQLAlchemy imprima todas las sentencias SQL
que ejecuta, lo cual es útil durante el desarrollo y la depuración.
"""

def create_db_and_tables():
    """
    Crea todas las tablas en la base de datos.

    Utiliza los metadatos de ``SQLModel`` para encontrar todas las definiciones
    de tablas (modelos) y las crea en la base de datos conectada
    a través del :data:`engine` si no existen previamente.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Generador de sesiones de base de datos.

    Proporciona una sesión de SQLAlchemy para interactuar con la base de datos.
    La sesión se cierra automáticamente al finalizar el bloque ``with``.

    :yields: Session: Una instancia de ``sqlmodel.Session``.
    :rtype: collections.abc.Generator[sqlmodel.Session, None, None]
    """
    with Session(engine) as session:
        yield session