from sqlalchemy import String, Text, DateTime, Integer, Float, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import datetime
from .base import Base, TimestampMixin
from models.astronomer import Astronomer
from models.celestial_body import CelestialBody


class Observation(Base, TimestampMixin):
    """
    Модель наблюдения.
    
    Связывает астронома с небесным телом и содержит детали наблюдения.
    Это промежуточная таблица для связи многие-ко-многим.
    """
    
    __tablename__ = "observations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Внешний ключ на астронома
    astronomer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("astronomers.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    # Внешний ключ на небесное тело
    celestial_body_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("celestial_bodies_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    obsevation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Дата и время наблюдения"
    )
    
    location: Mapped[Optional[str]] = mapped_column(
        String(200), 
        comment="Место наблюдения (абсерватория)"
    )
    equipment: Mapped[Optional[str]] = mapped_column(
        String(200), 
        comment="Используемое оборудование"
    )
    duration_hours: Mapped[Optional[float]] = mapped_column(
        Float,
        comment="Продолжительно наблюдения в часах"
    )
    weather_conditions: Mapped[Optional[str]] = mapped_column(
        String(100), 
        comment="Погодные условия"
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text, 
        comment="Заметки и комментарии"
    )
    data_collected: Mapped[Optional[str]] = mapped_column(
        Text, 
        comment="Научные данные"
    )
    
    
    # Связи relationship()
    astronomer: Mapped["Astronomer"] = relationship(
        "Astronomer",
        back_populates="observations",
        lazy="joined"
    )
    celestial_body: Mapped["CelestialBody"] = relationship(
        "CelestionBody",
        back_populates="observatrions",
        lazy="joined"
    )

    # Индексы для оптимизации запросов
    __table_args__ = (
        Index("idx_observation_date", "observation_date"),
        Index("idx_astronomer_celestial", "astronomer_id", "celestial_body_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<Observation(id={self.id}, "
            f"astronomer={self.astronomer_id}, "
            f"body={self.celestial_body_id}, "
            f"date={self.observation_date})>"
        )
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "astronomer_id": self.astronomer_id,
            "astronomer_name": self.astronomer.full_name if self.astronomer else None,
            "celestial_body_id": self.celestial_body_id,
            "celestial_body_name": self.celestial_body.name if self.celestial_body else None,
            "observation_date": self.observation_date.isoformat() if self.observation_date else None,
            "location": self.location,
            "equipment": self.equipment,
            "duration_hours": self.duration_hours,
            "weather_conditions": self.weather_conditions,
            "notes": self.notes,
            "data_collected": self.data_collected,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
