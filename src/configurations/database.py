import logging

from typing import AsyncGenerator, Callable, Optional
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.models.base import BaseModel
from src.configurations.settings import settings

# Список экспортируемых объектов модуля
__all__ = ["global_init", "get_async_session", "create_db_and_tables"]

# Логгер для записи ошибок и другой информации
logger = logging.getLogger(__name__)

# Глобальные переменные для управления подключением к базе данных
# __async_engine - движок взаимодействия с базой данных (создается один раз)
__async_engine: Optional[AsyncEngine] = None
# __session_factory - фабрика сессий для создания подключений к базе данных
__session_factory: Optional[Callable[[], AsyncSession]] = None


# URL для подключения к базе данных (формируется из настроек)
# Формат: postgresql+asyncpg://<username>:<password>@<host>:<port>/<database_name>.
# postgresql+asyncpg подключение по асинхронному коннектору, 
# postgres_user:postgres_pass из docker-compose
# 127.0.0.1:5445 адрес и внешний порт 
# fastapi_project_db название БД
SQLALCHEMY_DATABASE_URL = settings.database_url


def global_init() -> None:
    """
    Инициализирует глобальные объекты для работы с базой данных.
    Создает engine и session_factory, если они еще не созданы.
    """
    global __async_engine, __session_factory

    # Если session_factory уже инициализирована, выходим
    if __session_factory:
        return

    # Создаем engine, если он еще не создан
    if not __async_engine:
        __async_engine = create_async_engine(
            url=SQLALCHEMY_DATABASE_URL,
            echo=True,  # Логирование SQL-запросов в консоль (в продакшене лучше отключить)
        )

    # Создаем фабрику сессий
    __session_factory = async_sessionmaker(__async_engine)


async def get_async_session() -> AsyncGenerator:
    """
    Возвращает асинхронную сессию для работы с базой данных.
    Управляет транзакциями и обрабатывает исключения.

    Returns:
        AsyncGenerator: Асинхронный генератор, предоставляющий сессию.

    Raises:
        ValueError: Если global_init() не был вызван перед использованием.
    """
    global __session_factory

    # Проверяем, что global_init() был вызван
    if not __session_factory:
        raise ValueError(
            {"message": "You must call global_init() before using this method"}
        )

    # Создаем новую сессию
    session: AsyncSession = __session_factory()

    try:
        yield session  # Предоставляем сессию для использования
        await session.commit()  # Фиксируем изменения при успешном выполнении
    except Exception as e:
        logger.error("Raises exception: %s", e)  # Логируем ошибку
        raise e  # Передаем ошибку дальше
    finally:
        await session.rollback()  # Откатываем изменения в случае ошибки
        await session.close()  # Закрываем сессию


async def create_db_and_tables():
    """
    Создает таблицы в базе данных на основе метаданных моделей.
    """
    from src.models.books import Book
    from src.models.sellers import Seller

    global __async_engine

    # Проверяем, что global_init() был вызван
    if __async_engine is None:
        raise ValueError(
            {"message": "You must call global_init() before using this method"}
        )

    # Создаем таблицы в базе данных
    async with __async_engine.begin() as conn:  # Асинхронный контекстный менеджер
        await conn.run_sync(BaseModel.metadata.create_all)


async def delete_db_and_tables():
    """
    Удаляет все таблицы из базы данных.
    Используется только для тестирования или очистки.
    """
    global __async_engine

    # Проверяем, что global_init() был вызван
    if __async_engine is None:
        raise ValueError(
            {"message": "You must call global_init() before using this method"}
        )

    # Удаляем таблицы из базы данных
    async with __async_engine.begin() as conn:  # Асинхронный контекстный менеджер
        await conn.run_sync(BaseModel.metadata.drop_all)


