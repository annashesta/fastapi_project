from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from src.models.sellers import Seller
from src.schemes.sellers import IncomingSeller, ReturnedSeller, ReturnedSellerWithBooks
from src.configurations.database import get_async_session
from src.models.books import Book
from sqlalchemy.orm import selectinload

DBSession = AsyncSession

sellers_router = APIRouter(tags=["sellers"], prefix="/seller")


# 1. Регистрация продавца
@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)
async def create_seller(seller: IncomingSeller, session: DBSession = Depends(get_async_session)):
    new_seller = Seller(**seller.model_dump())
    session.add(new_seller)
    await session.flush()
    return new_seller


# 2. Получение списка всех продавцов
@sellers_router.get("/", response_model=List[ReturnedSeller])
async def get_all_sellers(session: DBSession = Depends(get_async_session)):
    query = select(Seller)
    result = await session.execute(query)
    sellers = result.scalars().all()
    return sellers


# 3. Получение данных о конкретном продавце и его книгах
@sellers_router.get("/{seller_id}", response_model=ReturnedSellerWithBooks)
async def get_seller(seller_id: int, session: DBSession = Depends(get_async_session)):
    # Явно загружаем связанные книги с помощью selectinload
    result = await session.execute(
        select(Seller).options(selectinload(Seller.books)).where(Seller.id == seller_id)
    )
    seller = result.scalars().first()

    # seller = await session.get(Seller.books, seller_id)
    if not seller:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return seller


# 4. Обновление данных продавца
@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, new_data: IncomingSeller, session: DBSession = Depends(get_async_session)):
    seller = await session.get(Seller, seller_id)
    if not seller:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    for key, value in new_data.model_dump().items():
        setattr(seller, key, value)
    await session.flush()
    return seller


# 5. Удаление продавца и его книг
@sellers_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, session: DBSession = Depends(get_async_session)):
    seller = await session.get(Seller, seller_id)
    if not seller:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    await session.delete(seller)
    return Response(status_code=status.HTTP_204_NO_CONTENT)