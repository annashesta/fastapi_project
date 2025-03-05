import pytest
from fastapi import status
from sqlalchemy import select
from src.models.sellers import Seller
from src.models.books import Book
from src.schemes.sellers import ReturnedSeller, ReturnedSellerWithBooks


# 1. Тест на регистрацию нового продавца
@pytest.mark.asyncio
async def test_create_seller(async_client):
    # Данные для создания нового продавца
    seller_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "password": "securepassword123",
    }

    # Отправляем POST-запрос
    response = await async_client.post("/api/v1/seller/", json=seller_data)

    # Проверяем статус ответа
    assert response.status_code == status.HTTP_201_CREATED

    # Проверяем, что данные продавца корректны
    result_data = response.json()
    assert result_data["first_name"] == seller_data["first_name"]
    assert result_data["last_name"] == seller_data["last_name"]
    assert result_data["email"] == seller_data["email"]
    assert "id" in result_data  # Убедимся, что ID был присвоен


# 2. Тест на попытку регистрации продавца с существующим email
@pytest.mark.asyncio
async def test_create_seller_with_existing_email(db_session, async_client):
    # Создаем продавца через базу данных
    existing_seller = Seller(
        first_name="John",
        last_name="Doe",
        email="existing.email@example.com",
        password="securepassword123",
    )
    db_session.add(existing_seller)
    await db_session.flush()

    # Пытаемся создать продавца с тем же email
    seller_data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "existing.email@example.com",
        "password": "anotherpassword",
    }
    response = await async_client.post("/api/v1/seller/", json=seller_data)

    # Проверяем, что сервер вернул ошибку 400
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already exists. Please use a different email."


# 3. Тест на получение списка всех продавцов
@pytest.mark.asyncio
async def test_get_all_sellers(db_session, async_client):
    # Создаем двух продавцов
    seller1 = Seller(
        first_name="John",
        last_name="Doe",
        email="1john.doe@example.com",
        password="password123",
    )
    seller2 = Seller(
        first_name="Jane",
        last_name="Doe",
        email="2jane.doe@example.com",
        password="password123",
    )
    db_session.add_all([seller1, seller2])
    await db_session.commit()

    # Выполняем запрос на получение всех продавцов
    response = await async_client.get("/api/v1/seller/")

    # Проверяем статус ответа
    assert response.status_code == status.HTTP_200_OK

    # Проверяем количество продавцов
    result_data = response.json()
    assert len(result_data) == 2
    
    
# 4. Тест на получение данных о конкретном продавце
@pytest.mark.asyncio
async def test_get_seller(db_session, async_client):
    # Создаем продавца через базу данных
    seller = Seller(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        password="securepassword123",
    )
    db_session.add(seller)
    await db_session.flush()

    # Получаем данные о продавце
    response = await async_client.get(f"/api/v1/seller/{seller.id}")

    # Проверяем статус ответа
    assert response.status_code == status.HTTP_200_OK

    # Проверяем, что данные продавца корректны
    result_data = response.json()
    assert result_data["id"] == seller.id
    assert result_data["first_name"] == seller.first_name
    assert result_data["last_name"] == seller.last_name
    assert result_data["email"] == seller.email
    assert "books" in result_data  # Убедимся, что поле books присутствует


# 5. Тест на получение несуществующего продавца
@pytest.mark.asyncio
async def test_get_not_seller(async_client):
    # Пытаемся получить несуществующего продавца
    response = await async_client.get("/api/v1/seller/999")

    # Проверяем, что сервер вернул ошибку 404
    assert response.status_code == status.HTTP_404_NOT_FOUND


# 6. Тест на обновление данных продавца
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    # Создаем продавца через базу данных
    seller = Seller(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        password="securepassword123",
    )
    db_session.add(seller)
    await db_session.flush()

    # Новые данные для обновления
    updated_data = {
        "first_name": "Jonathan",
        "last_name": "Smith",
        "email": "jonathan.smith@example.com",
        "password": "newpassword",
    }

    # Обновляем данные продавца
    response = await async_client.put(f"/api/v1/seller/{seller.id}", json=updated_data)

    # Проверяем статус ответа
    assert response.status_code == status.HTTP_200_OK

    # Проверяем, что данные обновились в базе
    updated_seller = await db_session.get(Seller, seller.id)
    assert updated_seller.first_name == updated_data["first_name"]
    assert updated_seller.last_name == updated_data["last_name"]
    assert updated_seller.email == updated_data["email"]
    assert updated_seller.password == updated_data["password"]


# 7. Тест на частичное обновление данных продавца (для этого тета даже добавила схему для частичного обновления)
@pytest.mark.asyncio
async def test_partial_update_seller(db_session, async_client, create_seller):
    seller = create_seller  # Используем фикстуру для создания продавца

    # Обновляем только одно поле
    updated_data = {
        "first_name": "Jonathan",
    }

    # Выполняем запрос на обновление
    response = await async_client.put(f"/api/v1/seller/{seller.id}", json=updated_data)

    # Проверяем статус ответа
    assert response.status_code == status.HTTP_200_OK

    # Проверяем, что только указанное поле обновилось
    updated_seller = await db_session.get(Seller, seller.id)
    assert updated_seller.first_name == updated_data["first_name"]
    assert updated_seller.last_name == seller.last_name  # Остальные поля не изменились
    assert updated_seller.email == seller.email
    
# 8. Тест на обновление несуществующего продавца
@pytest.mark.asyncio
async def test_update_nonexistent_seller(async_client):
    # Пытаемся обновить несуществующего продавца
    updated_data = {
        "first_name": "Jonathan",
        "last_name": "Smith",
        "email": "jonathan.smith@example.com",
        "password": "newpassword",
    }
    response = await async_client.put("/api/v1/seller/999", json=updated_data)

    # Проверяем, что сервер вернул ошибку 404
    assert response.status_code == status.HTTP_404_NOT_FOUND


# 9. Тест на удаление продавца
@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    # Создаем продавца через базу данных
    seller = Seller(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        password="securepassword123",
    )
    db_session.add(seller)
    await db_session.flush()

    # Удаляем продавца
    response = await async_client.delete(f"/api/v1/seller/{seller.id}")

    # Проверяем статус ответа
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Проверяем, что продавец удален из базы
    deleted_seller = await db_session.get(Seller, seller.id)
    assert deleted_seller is None


# 10. Тест на удаление несуществующего продавца
@pytest.mark.asyncio
async def test_delete_no_seller(async_client):
    # Пытаемся удалить несуществующего продавца
    response = await async_client.delete("/api/v1/seller/999")

    # Проверяем, что сервер вернул ошибку 404
    assert response.status_code == status.HTTP_404_NOT_FOUND


# 11. Тест на удаление продавца с книгами
@pytest.mark.asyncio
async def test_delete_seller_with_books(db_session, async_client):
    # Создаем продавца и связанную книгу через базу данных
    seller = Seller(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        password="securepassword123",
    )
    book = Book(
        title="Clean Code",
        author="Robert Martin",
        year=2021,
        pages=500,
        seller=seller,
    )
    db_session.add_all([seller, book])
    await db_session.flush()

    # Удаляем продавца
    response = await async_client.delete(f"/api/v1/seller/{seller.id}")

    # Проверяем статус ответа
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Проверяем, что продавец и его книги удалены из базы
    deleted_seller = await db_session.get(Seller, seller.id)
    assert deleted_seller is None

    deleted_book = await db_session.get(Book, book.id)
    assert deleted_book is None