from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel
# from .sellers import Seller ненужен, sqlalchemy  сама найдет модуль


class Book(BaseModel):
    """
    Модель книги.
    Представляет таблицу `books_table` в базе данных.
    """
    # Это будет табличка в БД
    __tablename__ = "books_table"
  
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False) # не может быть пустым
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int]
    pages: Mapped[int]
  
    # Связь с продавцом(один ко многим)
    seller_id: Mapped[int] = mapped_column(ForeignKey("sellers_table.id"), nullable=False)
    seller: Mapped["Seller"] = relationship("Seller", back_populates="books")
