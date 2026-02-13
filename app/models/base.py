"""
Базовый класс для всех моделей SQLAlchemy
Содержит общие поля и методы
"""

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func
from typing import Any


class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей.
    
    Использует новый стиль декларативных моделей SQLAlchemy 2.0.
    DeclarativeBase - базовый класс для декларативных моделей.
    """
    pass


class TimestampMixin:
    """
    Миксин для автоматическго добавление временных меток
    """
    craeted_ap: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # значение текущего времни по умолчанию на стороне сервера
        nullable=False
        )
    

    update_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),  # Автоматическое обнавление при изменении записи
        nullable=False
    )
    