"""
Модель астрономов.

Содержит информацию об ученых и их достижениях.
"""

from sqlalchemy import String, Integer, Date, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import date
from app.models.base import Base, TimestampMixin
from models.observation import Observation
from models.celestial_body import CelestialBody


class Astronomer(Base, TimestampMixin):
    """
    Модель астронома.

    Содержит информацию об ученом, его биографии и достижениях.
    """

    __tablename__ = "astronomers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    # Личная информация
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    # Полное имя (вычисляемое свойство)
    @property
    def full_name(self) -> str:
        """Полное имя астронома"""
        return f"{self.first_name} {self.last_name}"

    # Дата рождения
    birth_date: Mapped[Optional[date]] = mapped_column(Date)

    # Дата смерти (если применимо)
    death_date: Mapped[Optional[date]] = mapped_column(Date)

    # Национальность
    nationality: Mapped[Optional[str]] = mapped_column(String(100))

    # Биография
    biography: Mapped[Optional[str]] = mapped_column(Text)

    # Научные достижения
    achievements: Mapped[Optional[str]] = mapped_column(Text)

    # Известные открытия (через запятую)
    notable_discoveries: Mapped[Optional[str]] = mapped_column(Text)

    # Академическая степень
    academic_degree: Mapped[Optional[str]] = mapped_column(String(100))

    # Место работы
    institution: Mapped[Optional[str]] = mapped_column(String(200))

    # Активен ли астроном (жив/работает)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    # Связь "многие-ко-многим" с небесными телами через наблюдения
    observed_bodies: Mapped[List["CelestialBody"]] = relationship(
        "CelestialBody",
        secondary="observations",
        back_populates="observers",
        lazy="selectin"
    )

    # Связь с наблюдениями (один астроном - много наблюдений)
    observations: Mapped[List["Observation"]] = relationship(
        "Observation",
        back_populates="astronomer",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # ========== Вычисляемые свойства ==========

    @property
    def observation_count(self) -> int:
        """Количество наблюдений астронома"""
        return len(self.observations) if self.observations else 0

    @property
    def observed_bodies_count(self) -> int:
        """Количество наблюдавшихся тел"""
        return len(self.observed_bodies) if self.observed_bodies else 0

    @property
    def observed_bodies_list(self) -> List[dict]:
        """Список наблюдавшихся тел"""
        result = []
        for body in self.observed_bodies:
            result.append({
                "id": body.id,
                "name": body.name,
                "type": body.type.value
            })
        return result

    def __repr__(self) -> str:
        return f"<Astronomer(id={self.id}, name='{self.full_name}')>"
    
