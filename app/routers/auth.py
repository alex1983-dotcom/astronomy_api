"""
Маршрут для аутентификации.

Включает регистрацию, вход и работу с токенами JWT.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.database import get_db
from app.schemas.auth import (
    UserCreate,
    UserResponse,
    Token,
    UserLogin
)

# Настройки для JWT
SECRET_KEY = "your-secret-key-change-in-production-please-use-strong-random-string"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Настройки для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


router = APIRouter(
    prefix="/auth",
    tags=["Аутентификация"],
    responses={404: {"description": "Не найдено"}}
)


# ========== Вспомогательные функции ==========

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создание JWT токена"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Получение текущего пользователя из токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        # Теперь безопасно привести к типу str
        username_str: str = str(username)
    except JWTError:
        raise credentials_exception
    
    # Здесь должна быть логика получения пользователя из БД
    # Для примера возвращаем username
    return {"username": username_str}


# ========== Эндпоинты ==========

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя"
)
async def register_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Регистрация нового пользователя"""
    
    # Здесь должна быть логика проверки существования пользователя
    # и сохранения в БД
    
    # Для примера просто возвращаем данные
    return {
        "id": 1,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


@router.post(
    "/token",
    response_model=Token,
    summary="Получить токен доступа"
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Получение токена доступа по логину и паролю"""
    
    # Здесь должна быть логика аутентификации пользователя
    
    # Для примера создаем токен
    access_token = create_access_token(
        data={"sub": form_data.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Получить информацию о текущем пользователе"
)
async def read_users_me(
    current_user: dict = Depends(get_current_user)
):
    """Получение информации о текущем пользователе"""
    
    # Здесь должна быть логика получения пользователя из БД
    
    return {
        "id": 1,
        "username": current_user["username"],
        "email": f"{current_user['username']}@example.com",
        "full_name": None,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

