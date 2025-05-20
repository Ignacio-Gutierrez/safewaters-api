from sqlmodel import create_engine, Session, SQLModel
from app.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

connect_args = {}
if "sqlite" in SQLALCHEMY_DATABASE_URL.lower():
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    echo=True
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session