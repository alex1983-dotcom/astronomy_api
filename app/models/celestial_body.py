"""
Модель небесных тел (планеты, звезды, галактики)
Использует современный синтаксис SQLAlchemy 2.0
"""

from sqlalchemy import String, Float, Integer, Enum, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from enum import Enum as PyEnum
from .base import Base, TimestampMixin


# Перечисление типов небесных тел
class BodyType(PyEnum):
    """Типы небесных тел"""
    PLANET = "planet"
    STAR = "star"
    GALAXY = "galaxy"
    NEBULA = "nebula"
    COMET = "comet"
    ASTEROID = "asteroid"
    BLACK_HOLE = "black_hole"


# Перечисление спектральных классов звезд
class SpectralClass(PyEnum):
    """Спектральные классы звезд (последовательность Гарвардская)"""
    O = "O"  # Самые горячие (>30000K)
    B = "B"  # Горячие (10000-30000K)
    A = "A"  # Белые (7500-10000K)
    F = "F"  # Желто-белые (6000-7500K)
    G = "G"  # Желтые (5200-6000K) - как наше Солнце
    K = "K"  # Оранжевые (3700-5200K)
    M = "M"  # Красные (<3700K)


class CelestialBody(Base, TimestampMixin):
    """
    Модель небесного тела.
    
    Использует новый синтаксис mapped_column из SQLAlchemy 2.0.
    relationship() определяет связи между таблицами.
    """
    pass
