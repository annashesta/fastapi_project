from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Класс для хранения настроек приложения.
    Настройки загружаются из переменных окружения или файла `.env`.
    """
    
    # Настройки для подключения к PostgreSQL.
    db_host: str
    db_name: str
    db_username: str
    db_password: str
    db_test_name: str = "fastapi_project_test_db"
    max_connection_count: int = 25

    @property
    def database_url(self) -> str:
        """
        Возвращает URL для подключения к основной базе данных.

        Returns:
            str: URL в формате `postgresql+asyncpg://<username>:<password>@<host>/<database_name>`.
        """
        return f"postgresql+asyncpg://{self.db_username}:{self.db_password}@{self.db_host}/{self.db_name}"

    @property
    def database_test_url(self) -> str:
        """
        Возвращает URL для подключения к тестовой базе данных.

        Returns:
            str: URL в формате `postgresql+asyncpg://<username>:<password>@<host>/<database_name>`.
        """
        return f"postgresql+asyncpg://{self.db_username}:{self.db_password}@{self.db_host}/{self.db_test_name}"

    # Конфигурация для загрузки настроек из файла `.env`.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Экземпляр настроек, который будет использоваться в приложении.
settings = Settings()