"""
Модель пользователя для аутентификации.
"""

from sqlalchemy import String, Boolean, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from datetime import datetime
from .base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """
    Модель пользователя системы.
    
    Хранит данные для аутентификации и авторизации.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
        autoincrement=True
    )

    # Уникальное имя пользователя
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    # Email (уникальный)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    # Хешированный пароль (никогда не храним пароли в открытом виде!)
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Полное имя
    full_name: Mapped[Optional[str]] = mapped_column(
        String(100)
    )

    # Активен ли пользователь
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    # Суперпользователь (админ)
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    # Дополнительная информация
    bio: Mapped[Optional[str]] = mapped_column(Text)

    # Последний вход в систему
    last_login: Mapped[Optional[datetime]] = mapped_column()

    def verify_password(self, plain_password: str, pwd_context) -> bool:
        """
        Проверка пароля.
        
        Сравнивает переданный пароль с хешем в базе.
        """
        return pwd_context.verify(plain_password, self.hashed_password)

    def set_password(self, plain_password: str, pwd_context) -> None:
        """
        Установка нового пароля.
        
        Хеширует пароль и сохраняет хеш.
        """
        self.hashed_password = pwd_context.hash(plain_password)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"