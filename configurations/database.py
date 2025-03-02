import logging

from typing import AsyncGenerator, Callable, Optional
from  sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from models.base import BaseModel

__all__=["global_init", "get_async_session", "create_db_and_tables"]

logger = logging.getLogger("__name__")

# engine - движок взаимодействия между проектом и БД, создается 1 раз
# Типизацию мо/жно не расписывать  (Optional | None), но для совместимости:
# async_engine:  Это переменная проверки инициалаизации engine
__async_engine: Optional[AsyncEngine] = None
__session_factory: Optional[Callable[[], AsyncSession]] = None  # сессии подключений к БД


# postgresql+asyncpg подключение по асинхронному коннектору, 
# postgres_user:postgres_pass из docker-compose
# 127.0.0.1:5445 адрес и внешний порт 
# fastapi_project_db название БД
SQLALCHEMY_DATABASE_URL = (
    "postgresql+asyncpg://postgres_user:postgres_pass@127.0.0.1:5445/fastapi_project_db"
)


def global_init() -> None:
    global __async_engine, __session_factory

    if __session_factory:
        return

    if not __async_engine: 
        # создаем engine
        __async_engine = create_async_engine(url=SQLALCHEMY_DATABASE_URL, echo=True)
        # echo=True - для  логирования, дублирует все команды в консоль
        # В проде echo=False

    __session_factory = async_sessionmaker(__async_engine) # создаем сессию


async def get_async_session() -> AsyncGenerator:
    global __session_factory

    if not __session_factory:
        raise ValueError(
            {"message": "You must call global_init() before using this method"}
        )

    # Создаем конкретные сессии
    session: AsyncSession = __session_factory()

    try:
        yield session
        await session.commit()
    except Exception as e:
        logger.error("Raises exception: %s", e)
        raise e
    finally:
        await session.rollback()
        await session.close()


async def create_db_and_tables():
    '''Создает таблицы'''
    from models.books import Book

    global __async_engine

    if __async_engine is None:
        raise ValueError(
            {"message": "You must call global_init() before using this method"}
        )

    async with __async_engine.begin() as conn: # асинхронный менеджер контекста
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)
