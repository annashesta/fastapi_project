# Модуль для настройки маршрутов API.
# Этот файл объединяет все роутеры приложения и регистрирует их в основном роутере.

from fastapi import APIRouter

# Импортируем роутеры для книг и продавцов.
from .v1.books import books_router
from .v1.sellers import sellers_router

# Создаем основной роутер для версии API v1.
# Указываем тег "v1" и префикс "/api/v1" для всех маршрутов, зарегистрированных в этом роутере.
v1_router = APIRouter(tags=["v1"], prefix="/api/v1")

# Регистрируем роутеры для книг и продавцов.
v1_router.include_router(books_router)

v1_router.include_router(sellers_router)