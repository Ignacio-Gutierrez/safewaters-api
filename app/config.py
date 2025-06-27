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

    MONGODB_URL: str
    DATABASE_NAME: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configuración de correo electrónico
    SMTP_SERVER: str
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    FROM_EMAIL: str
    COMPANY_NAME: str = "SafeWaters"
    SMTP_USE_TLS: bool = True
    
    # URL del frontend para recuperación de contraseña
    FRONTEND_URL: str

    class Config:
        env_file = ".env"


settings = Settings()