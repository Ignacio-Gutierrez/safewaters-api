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

    class Config:
        env_file = ".env"


settings = Settings()