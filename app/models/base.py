"""
Базовый класс для всех моделей SQLAlchemy.

Содержит общие поля и методы, которые наследуются всеми моделями.
"""

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func
from typing import Any


class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей.

    Использует новый стиль декларативных моделей SQLAlchemy 2.0.
    DeclarativeBase - базовый класс для декларативных моделей.

    Пример использования:
        class User(Base):
            __tablename__ = "users"
            id: Mapped[int] = mapped_column(primary_key=True)
    """
    pass


class TimestampMixin:
    """
    Миксин для автоматического добавления временных меток.

    Добавляет поля created_at и updated_at в модели.
    Эти поля автоматически заполняются при создании и обновлении записей.

    Пример использования:
        class Article(Base, TimestampMixin):
            __tablename__ = "articles"
            id: Mapped[int] = mapped_column(primary_key=True)
            # created_at и updated_at добавятся автоматически
    """

    # Время создания записи
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Время последнего обновления записи
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    