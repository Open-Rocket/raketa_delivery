from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsDB(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DB_URL_asyncpg(self) -> str:
        """Возвращает строку подключения к базе данных для asyncpg"""

        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DB_URL_psycopg2(self) -> str:
        """Возвращает строку подключения к базе данных для psycopg2"""

        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


db_settings = SettingsDB()


__all__ = [
    "db_settings",
]
