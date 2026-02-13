"""
Docstring for app.database
Database and session configuration
Uses SQLAlchemy 2.0 with an asynchronous approach
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator
import os
from dotenv import load_dotenv


# Загрузка переменных окружения из .env файла
load_dotenv()

# URL подключения к базе данных
# asyncpg - асинхронный драйвер для PostgreSQL
# Для SQLite используем: sqlite+aiosqlite:///./astronomy.db
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "❌ DATABASE_URL не задан! Создай .env файл или установи переменную окружения."
        )

# Создание асинхронного движка (engine)
# echo=True - выводит все SQL запросы в консоль (полезно для отладки)
# poolclass=NullPool - отключает пул соединений (для тестов)
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,  # Использовать новый стиль SQLAlchemy 2.0
)


# Создание фабрики сессий
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,  # Ассихронная сессия
    expire_on_commit=False,  # Объекты остаются валидными после коммита
    autoflush=False,  # Автоматический flush отключен
)


# Используется в маршрутах через Depends(get_db)
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения асинхронной сессии базы данных.
    
    Использует контекстный менеджер для гарантии закрытия сессии.
    Даже если произойдет ошибка, сессия будет закрыта.
    
    Yields:
        AsyncSession: Асинхронная сессия SQLAlchemy
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit() # Коммитим измения если все успешно
        except Exception:
            await session.rollback()  # Откатываем изменения при ошибке
            raise
        finally:
            await session.close()  # Закрываем сессию

 
 
async def ini_db():
    """
    Инициализация базы данных: создание всех таблиц.
    
    Импортируем модели здесь, чтобы они были зарегистрированы в метаданных.
    Используем run_sync для выполнения синхронной операции в асинхронном контексте.
    """
    from models.base import Base
    from models import celestial_body, astronomer, observation

    async with engine.begin() as conn:
        # Создаем все таблицы определяемые в метаданных
        await conn.run_sync(Base.metadata.create_all)



