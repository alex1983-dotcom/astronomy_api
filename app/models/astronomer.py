"""
Модель астрономов
Содержит информацию об ученых и их достижениях
"""


from sqlalchemy import String, Integer, Date, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import date
from .base import Base, TimestampMixin
from models.observation import Observation
from models.celestial_body import CelestialBody


class Astronomer(Base, TimestampMixin):
    __tablename__ = "astronomers"

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        index=True
        )

    # Личная информация
    first_name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False, 
        comment="Имя"
        )
    last_name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False, 
        comment="Фамилия"
        )
    patronymic: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True, 
        comment="Отчество"
        )

    # Полное имя (вычесляемое свойство)
    @property
    def full_name(self) -> str:
        """Западный формат с отчеством в скобках при наличии"""
        name = f"{self.first_name} {self.last_name}"
        if self.patronymic:
            name += f" ({self.patronymic})"
        return name
        
    birth_date: Mapped[Optional[date]] = mapped_column(
        Date, 
        comment="Дата рождения"
        )
    death_date: Mapped[Optional[date]] = mapped_column(
        Date, 
        comment="Дата смерти"
        )
    nationality: Mapped[Optional[str]] = mapped_column(
        String(100), 
        comment="Национальность"
        )
    biography: Mapped[Optional[str]] = mapped_column(
        Text, 
        comment="Биография"
        )
    achievements: Mapped[Optional[str]] = mapped_column(
        Text, 
        comment="Научные достижения"
        )
    notable_discoveries: Mapped[Optional[str]] = mapped_column(
        Text, 
        comment="Известные открытия"
        )
    academic_degree: Mapped[Optional[str]] = mapped_column(
        String(100),
        comment="Акаемическая степень"
    )
    institution: Mapped[Optional[str]] = mapped_column(
        String(200),
        comment="Место работы"
        )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="Активен ли асторном(жив/работат)"
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
        lazy="dynamic"
    )   


