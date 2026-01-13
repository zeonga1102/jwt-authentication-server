
from pydantic import computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    class Config:
        env_file = ".env"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()
