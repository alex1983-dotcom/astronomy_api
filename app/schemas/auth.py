"""
Pydantic схемы для аутентификации.
"""

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime


class Token(BaseModel):
    """
    Схема для токена доступа.

    Используется для возврата JWT токена после аутентификации.
    """

    access_token: str = Field(..., description="JWT токен доступа")
    token_type: str = Field(default="bearer", description="Тип токена")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    }


class TokenData(BaseModel):
    """
    Схема для данных внутри токена.

    Содержит информацию, которая кодируется в JWT.
    """

    username: Optional[str] = None
    user_id: Optional[int] = None
    email: Optional[str] = None
    scopes: List[str] = Field(default_factory=list)

    model_config = {
        "from_attributes": True
    }


class UserBase(BaseModel):
    """
    Базовая схема пользователя.
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Имя пользователя"
    )

    email: EmailStr = Field(
        ...,
        description="Email пользователя"
    )

    full_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Полное имя"
    )

    model_config = {
        "from_attributes": True
    }


class UserCreate(UserBase):
    """
    Схема для создания пользователя.

    Добавляет поле пароля.
    """

    password: str = Field(
        ...,
        min_length=8,
        description="Пароль (минимум 8 символов)"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Валидация пароля"""
        if len(v) < 8:
            raise ValueError("Пароль должен быть минимум 8 символов")
        if not any(c.isupper() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        if not any(c.isdigit() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        return v


class UserUpdate(BaseModel):
    """
    Схема для обновления пользователя.
    """

    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8)

    model_config = {
        "from_attributes": True
    }


class UserResponse(UserBase):
    """
    Схема для ответа с информацией о пользователе.
    """

    id: int = Field(..., description="ID пользователя")
    is_active: bool = Field(..., description="Активен ли пользователь")
    created_at: datetime = Field(..., description="Время создания аккаунта")
    updated_at: datetime = Field(..., description="Время последнего обновления")

    model_config = {
        "from_attributes": True
    }


class UserLogin(BaseModel):
    """
    Схема для входа в систему.
    """

    username: str = Field(..., description="Имя пользователя или email")
    password: str = Field(..., description="Пароль")


class PasswordChange(BaseModel):
    """
    Схема для изменения пароля.
    """

    old_password: str = Field(..., description="Старый пароль")
    new_password: str = Field(..., min_length=8, description="Новый пароль")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        """Валидация нового пароля"""
        if len(v) < 8:
            raise ValueError("Новый пароль должен быть минимум 8 символов")
        if not any(c.isupper() for c in v):
            raise ValueError("Новый пароль должен содержать заглавную букву")
        if not any(c.isdigit() for c in v):
            raise ValueError("Новый пароль должен содержать цифру")
        return v