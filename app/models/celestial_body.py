"""
Модель небесных тел (планеты, звезды, галактики).

Использует современный синтаксис SQLAlchemy 2.0.
Содержит связи с другими моделями и вычисляемые свойства.
"""

from sqlalchemy import String, Float, Integer, Enum as SQLEnum, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from enum import Enum as PyEnum
from app.models.base import Base, TimestampMixin
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
    """
    Спектральные классы звезд (последовательность Гарвардская).

    Температурная шкала:
    - O: Самые горячие (>30000K)
    - B: Горячие (10000-30000K)
    - A: Белые (7500-10000K)
    - F: Желто-белые (6000-7500K)
    - G: Желтые (5200-6000K) - как наше Солнце
    - K: Оранжевые (3700-5200K)
    - M: Красные (<3700K)
    """
    O = "O"
    B = "B"
    A = "A"
    F = "F"
    G = "G"
    K = "K"
    M = "M"


class CelestialBody(Base, TimestampMixin):
    """
    Модель небесного тела.

    Использует новый синтаксис mapped_column из SQLAlchemy 2.0.
    relationship() определяет связи между таблицами.

    Структура:
    - Основная информация (название, тип, описание)
    - Физические характеристики (масса, радиус, температура)
    - Астрономические характеристики (звёздная величина, спектральный класс)
    - Координаты в небесной сфере
    - Связи с другими объектами (родитель, дети, наблюдения, наблюдатели)
    """

    __tablename__ = "celestial_bodies"

    # Первичный ключ
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    # Название небесного тела
    name: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        index=True,
        nullable=False
    )

    # Тип небесного тела (планета, звезда и т.д.)
    type: Mapped[BodyType] = mapped_column(
        SQLEnum(BodyType),
        nullable=False
    )

    # Описание
    description: Mapped[Optional[str]] = mapped_column(Text)

    # ========== Физические характеристики ==========

    # Масса в массах Солнца (для звезд) или Земли (для планет)
    mass: Mapped[Optional[float]] = mapped_column(Float)

    # Радиус в радиусах Солнца или Земли
    radius: Mapped[Optional[float]] = mapped_column(Float)

    # Температура поверхности в Кельвинах
    temperature: Mapped[Optional[float]] = mapped_column(Float)

    # Расстояние от Земли в световых годах
    distance_from_earth: Mapped[Optional[float]] = mapped_column(Float)

    # ========== Астрономические характеристики ==========

    # Спектральный класс (только для звезд)
    spectral_class: Mapped[Optional[SpectralClass]] = mapped_column(
        SQLEnum(SpectralClass)
    )

    # Абсолютная звёздная величина
    absolute_magnitude: Mapped[Optional[float]] = mapped_column(Float)

    # Видимая звёздная величина
    apparent_magnitude: Mapped[Optional[float]] = mapped_column(Float)

    # ========== Координаты в небесной сфере ==========

    # Прямое восхождение (часы, 0-24)
    right_ascension: Mapped[Optional[float]] = mapped_column(Float)

    # Склонение (градусы, -90 до 90)
    declination: Mapped[Optional[float]] = mapped_column(Float)

    # ========== Связи с другими объектами ==========

    # Связь с родительским телом (например, планета -> звезда)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("celestial_bodies.id"),
        nullable=True
    )

    # Связь "многие-ко-многим" с астрономами через таблицу наблюдений
    observers: Mapped[List["Astronomer"]] = relationship(
        "Astronomer",
        secondary="observations",
        back_populates="observed_bodies",
        lazy="selectin"
    )

    # Связь с дочерними телами (спутники планеты, планеты звезды)
    children: Mapped[List["CelestialBody"]] = relationship(
        "CelestialBody",
        foreign_keys="[CelestialBody.parent_id]",
        back_populates="parent",
        lazy="selectin"
    )

    # Обратная связь к родителю
    parent: Mapped[Optional["CelestialBody"]] = relationship(
        "CelestialBody",
        foreign_keys="[CelestialBody.parent_id]",
        remote_side="[CelestialBody.id]",
        back_populates="children",
        lazy="select"
    )

    # Связь с наблюдениями (одно тело - много наблюдений)
    observations: Mapped[List["Observation"]] = relationship(
        "Observation",
        back_populates="celestial_body",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # ========== Индексы для оптимизации запросов ==========

    __table_args__ = (
        Index("idx_type_distance", "type", "distance_from_earth"),
        Index("idx_magnitude", "apparent_magnitude"),
    )

    # ========== Вычисляемые свойства (для использования в схемах) ==========

    @property
    def parent_name(self) -> Optional[str]:
        """
        Название родительского тела.

        Это вычисляемое свойство, которое возвращает имя родителя.
        Используется в Pydantic схемах для сериализации.

        Возвращает:
            str или None: Название родителя или None, если родителя нет
        """
        return self.parent.name if self.parent else None

    @property
    def children_count(self) -> int:
        """
        Количество дочерних тел.

        Возвращает:
            int: Количество детей (0 если нет)
        """
        return len(self.children) if self.children else 0

    @property
    def observation_count(self) -> int:
        """
        Количество наблюдений этого тела.

        Возвращает:
            int: Количество наблюдений (0 если нет)
        """
        return len(self.observations) if self.observations else 0

    @property
    def observers_list(self) -> List[dict]:
        """
        Список астрономов, наблюдавших это тело.

        Возвращает:
            List[dict]: Список словарей с информацией об астрономах
        """
        result = []
        for observer in self.observers:
            result.append({
                "id": observer.id,
                "name": observer.full_name,
                "institution": observer.institution
            })
        return result

    # ========== Методы для отладки и сериализации ==========

    def __repr__(self) -> str:
        """
        Строковое представление объекта для отладки.

        Возвращает:
            str: Строка в формате <CelestialBody(id=1, name='Солнце', type=star)>
        """
        return f"<CelestialBody(id={self.id}, name='{self.name}', type={self.type.value})>"


# Создание дополнительных индексов
Index("idx_celestial_body_type", CelestialBody.type)
Index("idx_celestial_body_name", CelestialBody.name)

