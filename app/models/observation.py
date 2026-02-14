"""
Модель наблюдений астрономов за небесными телами.

Промежуточная таблица для связи многие-ко-многим.
"""

from sqlalchemy import String, Text, DateTime, Integer, Float, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import datetime
from app.models.base import Base, TimestampMixin
from models.astronomer import Astronomer
from models.celestial_body import CelestialBody



class Observation(Base, TimestampMixin):
    """
    Модель наблюдения.

    Связывает астронома с небесным телом и содержит детали наблюдения.
    Это промежуточная таблица для связи многие-ко-многим.
    """

    __tablename__ = "observations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    # Внешний ключ на астронома
    astronomer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("astronomers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Внешний ключ на небесное тело
    celestial_body_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("celestial_bodies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Дата и время наблюдения
    observation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    # Место наблюдения (обсерватория)
    location: Mapped[Optional[str]] = mapped_column(String(200))

    # Используемое оборудование
    equipment: Mapped[Optional[str]] = mapped_column(String(200))

    # Продолжительность наблюдения в часах
    duration_hours: Mapped[Optional[float]] = mapped_column(Float)

    # Погодные условия
    weather_conditions: Mapped[Optional[str]] = mapped_column(String(100))

    # Заметки и комментарии
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Научные данные
    data_collected: Mapped[Optional[str]] = mapped_column(Text)

    # Связь с астрономом
    astronomer: Mapped["Astronomer"] = relationship(
        "Astronomer",
        back_populates="observations",
        lazy="joined"
    )

    # Связь с небесным телом
    celestial_body: Mapped["CelestialBody"] = relationship(
        "CelestialBody",
        back_populates="observations",
        lazy="joined"
    )

    # Индексы для оптимизации запросов
    __table_args__ = (
        Index("idx_observation_date", "observation_date"),
        Index("idx_astronomer_celestial", "astronomer_id", "celestial_body_id"),
    )

    # ========== Вычисляемые свойства ==========

    @property
    def astronomer_name(self) -> Optional[str]:
        """Имя астронома"""
        return self.astronomer.full_name if self.astronomer else None

    @property
    def celestial_body_name(self) -> Optional[str]:
        """Название небесного тела"""
        return self.celestial_body.name if self.celestial_body else None

    def __repr__(self) -> str:
        return (
            f"<Observation(id={self.id}, "
            f"astronomer={self.astronomer_id}, "
            f"body={self.celestial_body_id}, "
            f"date={self.observation_date})>"
        )
    


