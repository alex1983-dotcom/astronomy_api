"""
Маршрут для аутентификации.

Включает регистрацию, вход и работу с токенами JWT.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import bcrypt

from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    UserCreate,
    UserResponse,
    Token,
    UserUpdate,
    PasswordChange
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
    """
    Проверка пароля.
    
    Поддерживает хеши от bcrypt и старые хеши от passlib.
    """
    # Обрезаем пароль до 72 байт (ограничение bcrypt)
    password_bytes = plain_password.encode('utf-8')[:72]
    
    try:
        # Проверяем через прямой bcrypt (новые пользователи)
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except ValueError:
        # Если ошибка — пробуем через passlib (старые пользователи)
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Хеширование пароля.
    
    Преобразует пароль в безопасный хеш для хранения в базе данных.
    
    **Параметры:**
    - `password`: пароль в открытом виде
    
    **Возвращает:**
    - `str`: хешированный пароль
    """
    password_bytes = password.encode('utf-8')[:72]  # Обрезаем до 72 байт
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создание JWT токена доступа.
    
    Генерирует токен с указанными данными и временем жизни.
    
    **Параметры:**
    - `data`: данные для кодирования в токен (например, имя пользователя)
    - `expires_delta`: время жизни токена (по умолчанию 30 минут)
    
    **Возвращает:**
    - `str`: JWT токен
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Получение текущего пользователя из токена.
    
    Декодирует JWT токен и получает пользователя из базы данных.
    Используется как зависимость для защищенных эндпоинтов.
    
    **Параметры:**
    - `token`: JWT токен из заголовка Authorization
    - `db`: асинхронная сессия базы данных
    
    **Возвращает:**
    - `User`: объект пользователя из базы данных
    
    **Исключения:**
    - `HTTPException`: если токен недействителен или пользователь не найден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Декодирование токена
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Получение имени пользователя из токена
        username: Optional[str] = payload.get("sub")
        
        if username is None:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    # Поиск пользователя в базе данных
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь неактивен"
        )
    
    return user


# ========== Эндпоинты ==========

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
    description="Создает нового пользователя в системе"
)
async def register_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Регистрация нового пользователя.
    
    Создает нового пользователя с хешированным паролем.
    
    **Параметры:**
    - `user`: данные для регистрации (имя пользователя, email, пароль)
    - `db`: асинхронная сессия базы данных
    
    **Возвращает:**
    - `UserResponse`: созданный пользователь
    
    **Исключения:**
    - `HTTPException`: если пользователь с таким именем или email уже существует
    """
    
    # Проверка существования пользователя с таким именем
    query = select(User).where(User.username == user.username)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    
    # Проверка существования пользователя с таким email
    query = select(User).where(User.email == user.email)
    result = await db.execute(query)
    existing_email = result.scalar_one_or_none()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Хеширование пароля
    hashed_password = get_password_hash(user.password)
    
    # Создание нового пользователя
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_active=True,
        is_superuser=False
    )
    
    # Добавление в сессию
    db.add(db_user)
    
    # Фиксация изменений
    await db.commit()
    
    # Обновление объекта
    await db.refresh(db_user)
    
    return db_user


@router.post(
    "/token",
    response_model=Token,
    summary="Получить токен доступа",
    description="Аутентификация пользователя и получение JWT токена"
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение токена доступа по логину и паролю.
    
    Проверяет учетные данные и возвращает JWT токен.
    
    **Параметры:**
    - `form_data`: форма с именем пользователя и паролем
    - `db`: асинхронная сессия базы данных
    
    **Возвращает:**
    - `Token`: JWT токен доступа
    
    **Исключения:**
    - `HTTPException`: если имя пользователя или пароль неверны
    """
    
    # Поиск пользователя по имени
    query = select(User).where(User.username == form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    # Проверка существования и активности
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверка пароля
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Конвертируем в naive datetime для совместимости с TIMESTAMP WITHOUT TIME ZONE
    user.last_login = datetime.now(timezone.utc).replace(tzinfo=None)
    await db.commit()
    
    # Создание токена
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Получить информацию о текущем пользователе",
    description="Возвращает данные авторизованного пользователя"
)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    """
    Получение информации о текущем пользователе.
    
    Требует аутентификации через JWT токен.
    
    **Параметры:**
    - `current_user`: зависимость, получающая пользователя из токена
    
    **Возвращает:**
    - `UserResponse`: данные текущего пользователя
    """
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Обновить информацию о текущем пользователе",
    description="Обновляет данные авторизованного пользователя"
)
async def update_users_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление информации о текущем пользователе.
    
    Позволяет изменить данные пользователя (кроме пароля).
    
    **Параметры:**
    - `user_update`: данные для обновления
    - `current_user`: зависимость, получающая пользователя из токена
    - `db`: асинхронная сессия базы данных
    
    **Возвращает:**
    - `UserResponse`: обновленные данные пользователя
    
    **Исключения:**
    - `HTTPException`: если новый email уже используется другим пользователем
    """
    
    # Проверка уникальности email при его изменении
    if user_update.email and user_update.email != current_user.email:
        query = select(User).where(
            User.email == user_update.email,
            User.id != current_user.id
        )
        result = await db.execute(query)
        existing_email = result.scalar_one_or_none()
        
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email уже используется другим пользователем"
            )
    
    # Обновление полей
    update_data = user_update.model_dump(exclude_unset=True, exclude={"password"})
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    # Если указан новый пароль
    if user_update.password:
        current_user.hashed_password = get_password_hash(user_update.password)
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.post(
    "/me/change-password",
    summary="Изменить пароль",
    description="Изменяет пароль текущего пользователя"
)
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Изменение пароля текущего пользователя.
    
    Требует ввода старого пароля для подтверждения.
    
    **Параметры:**
    - `password_change`: данные для изменения пароля
    - `current_user`: зависимость, получающая пользователя из токена
    - `db`: асинхронная сессия базы данных
    
    **Возвращает:**
    - `dict`: сообщение об успешном изменении
    
    **Исключения:**
    - `HTTPException`: если старый пароль неверен
    """
    
    # Проверка старого пароля
    if not verify_password(password_change.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный старый пароль"
        )
    
    # Установка нового пароля
    current_user.hashed_password = get_password_hash(password_change.new_password)
    
    await db.commit()
    
    return {"message": "Пароль успешно изменен"}

