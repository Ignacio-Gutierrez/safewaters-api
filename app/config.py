from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MEMCACHED_HOST: str
    MEMCACHED_PORT: int
    MEMCACHED_TIMEOUT: int = 86400

    URLSCANIO_API_KEY: str
    URLSCANIO_API_URL: str

    THREATFOX_API_KEY: str
    THREATFOX_API_URL: str

    ABUSEIPDB_API_KEY: str
    ABUSEIPDB_API_URL: str

    # Variables para la BD y JWT
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"


settings = Settings()