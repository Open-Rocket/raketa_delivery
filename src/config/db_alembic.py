from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsDB(BaseSettings):
    DB_HOST_DEV: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DB_URL_asyncpg_dev(self) -> str:
        """Возвращает строку подключения к базе данных для asyncpg"""

        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST_DEV}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env.dev", extra="allow")


db_settings_dev = SettingsDB()


__all__ = ["db_settings_dev"]
