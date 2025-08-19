from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "ELibrary API"
    MONGO_URI: str
    MONGO_DB: str

    class Config:
        env_file = ".env"  # Loads variables from .env file

settings = Settings()
