from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsDB_ALEMBIC(BaseSettings):
    DB_HOST_ORIGINAL: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DB_URL_asyncpg_alembic(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST_ORIGINAL}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env.local", extra="ignore")


db_settings_alembic = SettingsDB_ALEMBIC()

__all__ = ["db_settings_alembic"]
