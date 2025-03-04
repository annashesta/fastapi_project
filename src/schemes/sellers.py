from pydantic import BaseModel, EmailStr, Field
from typing import List

from .books import Returnedbook

__all__ = ["IncomingSeller", "ReturnedSeller", "ReturnedSellerWithBooks"]

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