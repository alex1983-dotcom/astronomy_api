from sqlalchemy import String, Text, DateTime, Integer, Float, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import datetime
from .base import Base, TimestampMixin


class Observation(Base, TimestampMixin):
    """
    Модель наблюдения.
    
    Связывает астронома с небесным телом и содержит детали наблюдения.
    Это промежуточная таблица для связи многие-ко-многим.
    """
    pass