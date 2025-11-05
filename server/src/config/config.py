from pydantic_settings import BaseSettings
from dotenv import dotenv_values

env = dotenv_values("./.env")

class CommonSettings(BaseSettings):
     API_VERSION_STR: str = "/api_v1"
     API_VERSION: str = "1.0.0"
     APP_NAME: str = env.get('PROJECT_NAME')
     DEBUG_MODE: bool = True
     JWT_SECRET_KEY: str = env.get("JWT_SECRET_KEY")
     ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
     REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
     
     class Config:
          case_sensitive = True


class ServerSettings(BaseSettings):
     HOST: str = env.get('HOST')
     PORT: int = env.get('PORT')
     
     class Config:
          case_sensitive = True

class DatabaseSettings(BaseSettings):
     DB_URI: str = env.get('MONGO_URI')
     DB_NAME: str = env.get('DB_NAME')
     
     class Config:
          case_sensitive = True

class GitHubSettings(BaseSettings):
     GITHUB_API_TOKEN: str = env.get('GITHUB_API_TOKEN', '')
     GITHUB_API_VERSION: str = "2022-11-28"
     GITHUB_TIMEOUT: int = 10
     GITHUB_CACHE_TTL: int = 86400  # 24 hours in seconds
     
     class Config:
          case_sensitive = True

class Settings(CommonSettings, ServerSettings, DatabaseSettings, GitHubSettings):
     pass


settings = Settings()