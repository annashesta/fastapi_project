from pydantic import BaseModel, EmailStr, Field
from typing import List

from .books import Returnedbook

__all__ = ["IncomingSeller", "ReturnedSeller", "ReturnedSellerWithBooks", "UpdateSeller"]

class IncomingSeller(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class ReturnedSeller(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


class ReturnedSellerWithBooks(ReturnedSeller):
    books: List[Returnedbook] = []


# Схема для частичного обновления, здесь все поля являются опциональными (None по умолчанию):
class UpdateSeller(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    password: str | None = None