from sqlalchemy.orm import DeclarativeBase

class BaseModel(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.
    Наследуется от `DeclarativeBase`, что позволяет использовать декларативный стиль
    для определения моделей (таблиц) в базе данных.
    Не содержит дополнительной логики, поэтому используется ключевое слово pass, чтобы избежать ошибок синтаксиса.
    """
    pass