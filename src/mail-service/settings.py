from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    x_api_key: str = Field(..., alias="X_API_KEY")

    class Config:
        env_file = ".env"


Settings_ = Settings()
