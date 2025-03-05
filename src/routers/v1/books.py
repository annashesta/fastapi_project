# Для импорта из корневого модуля
# import sys
# sys.path.append("..")
# from main import app

# Модуль для работы с книгами.
# Этот файл содержит роутеры для выполнения CRUD-операций с книгами.
# CRUD - Create, Read, Update, Delete

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import field_validator
from pydantic_core import PydanticCustomError
from sqlalchemy import select

from src.models.books import Book
from src.models.sellers import Seller  # Импортируем модель Seller
from src.schemes import IncomingBook, Returnedbook, ReturnedAllbooks
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession
from src.configurations import get_async_session

# Создаем роутер для книг.
books_router = APIRouter(tags=["books"], prefix="/books")

# Определяем тип DBSession для инъекции зависимости.
# Это асинхронная сессия, которая будет автоматически создаваться и управляться FastAPI.
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка для создания записи о книге в базе данных.
# @books_router.post("/books/", status_code=status.HTTP_201_CREATED)
@books_router.post("/", response_model=Returnedbook, status_code=status.HTTP_201_CREATED)
async def create_book(
    book: IncomingBook,
    session: DBSession,
):
    """
    Создает новую книгу в базе данных.
    Если продавец с указанным seller_id не существует, возвращает ошибку 404.
    """
    # Проверяем, существует ли продавец с указанным seller_id.
    seller = await session.get(Seller, book.seller_id)
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Seller with id {book.seller_id} not found.",
        )

    # Создаем объект книги на основе входных данных.
    new_book = Book(
        title=book.title,
        author=book.author,
        year=book.year,
        pages=book.pages,
        seller_id=book.seller_id,
    )

    # Добавляем книгу в сессию.
    session.add(new_book)
    await session.flush()  # Фиксируем изменения в базе данных и получаем ID книги.

    # Возвращаем созданную книгу.
    return new_book

# Ручка для получения списка всех книг.
@books_router.get("/", response_model=ReturnedAllbooks)
async def get_all_books(session: DBSession):
    """
    Возвращает список всех книг из базы данных.
    """
    # Формируем SQL-запрос для получения всех книг.
    # Хотим видеть формат
    # books: [{"id": 1, "title":"blabla",..., "year": 2023}, {...}]
    query = select(Book) # SELECT * FROM book
    result = await session.execute(query)
    books = result.scalars().all()  # Получаем все книги.
    
    # Возвращаем список книг в формате, указанном в схеме ReturnedAllbooks.
    return {"books": books}


# Ручка для получения книги по её ID.
@books_router.get("/{book_id}", response_model=Returnedbook)
async def get_book(book_id: int, session: DBSession):
    """
    Возвращает книгу по её ID.
    Если книга не найдена, возвращает статус 404.
    """
    # Ищем книгу по ID.
    if result := await session.get(Book, book_id):
        return result  # Возвращаем найденную книгу.
    
    return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для удаления книги по её ID.
@books_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, session: DBSession):
    """
    Удаляет книгу по её ID.
    Если книга не найдена, возвращает статус 404.
    """
    # Ищем книгу по ID.
    deleted_book = await session.get(Book, book_id)
    ic(deleted_book)  # Логируем информацию о книге для отладки.
    
    if deleted_book:
        await session.delete(deleted_book)
        await session.commit()  # Фиксируем изменения в базе данных
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для обновления данных о книге по её ID.
@books_router.put("/{book_id}", response_model=Returnedbook, status_code=status.HTTP_200_OK )
async def update_book(book_id: int, new_book_data: Returnedbook, session: DBSession):
    """
    Обновляет данные о книге по её ID.
    Если книга не найдена, возвращает статус 404.
    """
    # Ищем книгу по ID.
    if updated_book := await session.get(Book, book_id):
        # Обновляем данные книги.
        updated_book.author = new_book_data.author
        updated_book.title = new_book_data.title
        updated_book.year = new_book_data.year
        updated_book.pages = new_book_data.pages
        
        await session.flush()  # Фиксируем изменения в базе данных.
        
        return updated_book
        
    return Response(status_code=status.HTTP_404_NOT_FOUND)