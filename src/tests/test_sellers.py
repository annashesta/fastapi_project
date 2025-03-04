import pytest
from fastapi import status
from sqlalchemy import select
from src.models.sellers import Seller
from src.models.books import Book


@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "password": "password123"
    }
    response = await async_client.post("/api/v1/seller/", json=data)
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.json()


@pytest.mark.asyncio
async def test_get_all_sellers(db_session, async_client):
    seller = Seller(first_name="Jane", last_name="Doe", email="jane.doe@example.com", password="password123")
    db_session.add(seller)
    await db_session.flush()

    response = await async_client.get("/api/v1/seller/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0


@pytest.mark.asyncio
async def test_get_seller_with_books(db_session, async_client):
    seller = Seller(first_name="Alice", last_name="Smith", email="alice.smith@example.com", password="password123")
    book = Book(title="Book Title", author="Author", year=2023, pages=300, seller=seller)
    db_session.add_all([seller, book])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/seller/{seller.id}")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["books"]) == 1


@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    seller = Seller(first_name="Bob", last_name="Johnson", email="bob.johnson@example.com", password="password123")
    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/seller/{seller.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT