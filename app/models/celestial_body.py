"""
Модель небесных тел (планеты, звезды, галактики)
Использует современный синтаксис SQLAlchemy 2.0
"""

from sqlalchemy import String, Float, Integer, Enum, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from enum import Enum as PyEnum
from .base import Base, TimestampMixin
from models.astronomer import Astronomer
from models.observation import Observation

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
    __tablename__ = "celestial_bodies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=False, 
                                      comment="Название небесного тела")
    type: Mapped[str] = mapped_column(Enum(BodyType), nullable=False,
                                      comment="Тип небесного тела")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="Описание")

    # Физические характеристики
    mass: Mapped[Optional[float]] = mapped_column(
        Float, comment="Масса в массах Солнца (для звезд) или Земли (для планет)"
    )
    radius: Mapped[Optional[float]] = mapped_column(
        Float, comment="Радиус в радиусах солнца или Земли"
    )
    temperature: Mapped[Optional[float]] = mapped_column(
        Float, comment="Температура поверхности в Кельвинах"
    )
    distance_from_earth: Mapped[Optional[float]] = mapped_column(
        Float, comment="Расстояние от земли в световых годах"
    )
    
    # Астрономические характеристики
    spectra_class: Mapped[Optional[SpectralClass]] = mapped_column(
        Enum(SpectralClass)
    )
    absolute_magnitude: Mapped[Optional[float]] = mapped_column(
        Float, comment="Абсолютная звездная величина"
    )
    apparent_magnitude: Mapped[Optional[float]] = mapped_column(
        Float, command="Видимая звездная величина"
    )

    # Кооринаты в небесной сфере
    right_ascension: Mapped[Optional[float]] = mapped_column(
        Float, comment="Прямое восхождение (часы)"
    )
    declination: Mapped[Optional[float]] = mapped_column(
        Float, comment="Склонение (градусы)"
    )
    
    # Связь с родительским телом (например, планета -> звезда)
    # самоссылающаяся связь (self-referential relationship)
    parent_id: Mapped[Mapped[int]] = mapped_column(
        Integer,
        ForeignKey("celestial_bodies.id"),
        nullable=True
    )

    # Связь многие-ко-многим с астрономами через таблицу наблюдений
    observers: Mapped[List["Astronomer"]] = relationship(
        "Astronomer",
        secondary="observations",
        back_populates="observed_bodies",
        lazy="selectin"
    )
    # Связь с дочерними телами (спутники планеты, планеты звезды)
    children: Mapped[List["CelestialBody"]] = relationship(
        "CelestialBody",
        backref="parent", # Автоматически создет обратную связь
        remote_side=[id], # Указывает на "удаленую сторону" (рекурсивая связь)
        lazy="joined" # Згружает связанные данные в одном запросе
    )
    # Связь с наблюдениями
    observations: Mapped[List["Observation"]] = relationship(
        "Observantin",
        back_populates="celestial_body",
        cascade="all, delete-orphan", # Каскадное удаление
        lazy="dynamic" # Ленивая загрузка с возможностью фильтрации
    )
    # Индексы для оптимизации запросов
    __table_args__ = (
        Index("idx_type_distance", "type", "distance_from_earth"),
        Index("idx_magnitude", "apparent_magnitude"),
    )

    def __repr__(self) -> str:
        return f"<CelestialBody(id={self.id}, name='{self.name}', type={self.type.value})>"
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "mass": self.mass,
            "radius": self.radius,
            "temperature": self.temperature,
            "distance_from_earth": self.distance_from_earth,
            "spectral_class": self.spectral_class.value if self.spectral_class else None,
            "absolute_magnitude": self.absolute_magnitude,
            "apparent_magnitude": self.apparent_magnitude,
            "right_ascension": self.right_ascension,
            "declination": self.declination,
            "parent_id": self.parent_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
# Создание индексов для оптимизации запросов
# Индексы ускоряют поиск по часто используемым полям
Index("idx_celestial_body_type", CelestialBody.type)
Index("idx_celestial_body_name", CelestialBody.name)

