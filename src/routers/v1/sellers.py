# Модуль для работы с продавцами.
# Этот файл содержит роутеры для выполнения CRUD-операций с продавцами.


from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from typing import List

from src.models.sellers import Seller
from src.schemes.sellers import IncomingSeller, ReturnedSeller, ReturnedSellerWithBooks, UpdateSeller
from src.configurations.database import get_async_session
from src.models.books import Book
from sqlalchemy.orm import selectinload  # Для загрузки связанных данных.

# Определяем тип DBSession для инъекции зависимости.
DBSession = AsyncSession

# Создаем роутер для продавцов.
sellers_router = APIRouter(tags=["sellers"], prefix="/seller")


# 1. Регистрация продавца
@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)
async def create_seller(
    seller: IncomingSeller,   # Входные данные, валидируемые схемой IncomingSeller.
    session: DBSession = Depends(get_async_session) # Асинхронная сессия для работы с базой данных.
    ):
    """
    Создает нового продавца в базе данных.
    Если email уже существует, возвращает ошибку 400.
    """
    try:
        # Создаем объект продавца на основе входных данных.
        new_seller = Seller(**seller.model_dump())

        # Добавляем продавца в сессию.
        session.add(new_seller)
        await session.flush()  # Фиксируем изменения в базе данных и получаем ID продавца.

        # Возвращаем созданного продавца.
        return new_seller

    except IntegrityError as e:
        # Если возникает ошибка уникальности (например, email уже существует),
        # откатываем транзакцию и возвращаем ошибку 400.
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists. Please use a different email.",
        )



# 2. Получение списка всех продавцов
@sellers_router.get("/", response_model=List[ReturnedSeller])
async def get_all_sellers(
    session: DBSession = Depends(get_async_session)
    ):
    """
    Возвращает список всех продавцов из базы данных.
    """
    # Формируем SQL-запрос для получения всех продавцов.
    query = select(Seller)
    result = await session.execute(query)
    sellers = result.scalars().all()
    return sellers


# 3. Получение данных о конкретном продавце и его книгах
@sellers_router.get("/{seller_id}", response_model=ReturnedSellerWithBooks)
async def get_seller(
    seller_id: int, 
    session: DBSession = Depends(get_async_session)
    ):
    """
    Возвращает данные о продавце и его книгах по ID продавца.
    Если продавец не найден, возвращает статус 404.
    """
    # Явно загружаем связанные книги с помощью selectinload
    result = await session.execute(
        select(Seller).options(selectinload(Seller.books)).where(Seller.id == seller_id)
    )
    seller = result.scalars().first()

    if not seller:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return seller


# 4. Обновление данных продавца
@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(
    seller_id: int,
    new_data: UpdateSeller,  # Используем новую схему
    session: DBSession = Depends(get_async_session),
):
    """
    Обновляет данные о продавце по его ID.
    Если продавец не найден, возвращает статус 404.
    """
    seller = await session.get(Seller, seller_id)
    if not seller:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    # Обновляем только те поля, которые были переданы
    for key, value in new_data.model_dump(exclude_unset=True).items():
        setattr(seller, key, value)

    await session.flush()
    return seller


# 5. Удаление продавца и его книг
@sellers_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(
    seller_id: int, 
    session: DBSession = Depends(get_async_session)
):
    """
    Удаляет продавца и его книги по ID продавца.
    Если продавец не найден, возвращает статус 404.
    """
    seller = await session.get(Seller, seller_id)
    if not seller:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    
    await session.delete(seller)
    await session.commit()  # Фиксируем изменения
    return Response(status_code=status.HTTP_204_NO_CONTENT)