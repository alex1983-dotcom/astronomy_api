"""
Pydantic схемы для наблюдений.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class ObservationBase(BaseModel):
    """
    Базовая схема наблюдения.
    """

    astronomer_id: int = Field(
        ...,
        ge=1,
        description="ID астронома"
    )

    celestial_body_id: int = Field(
        ...,
        ge=1,
        description="ID небесного тела"
    )

    observation_date: datetime = Field(
        ...,
        description="Дата и время наблюдения"
    )

    location: Optional[str] = Field(
        None,
        max_length=200,
        description="Место наблюдения"
    )

    equipment: Optional[str] = Field(
        None,
        max_length=200,
        description="Используемое оборудование"
    )

    duration_hours: Optional[float] = Field(
        None,
        ge=0,
        description="Продолжительность в часах"
    )

    weather_conditions: Optional[str] = Field(
        None,
        max_length=100,
        description="Погодные условия"
    )

    notes: Optional[str] = Field(
        None,
        description="Заметки и комментарии"
    )

    data_collected: Optional[str] = Field(
        None,
        description="Научные данные"
    )

    @field_validator("observation_date")
    @classmethod
    def validate_observation_date(cls, v):
        """Проверка, что дата наблюдения не в будущем"""
        now = datetime.now(v.tzinfo) if v.tzinfo else datetime.now()
        if v > now:
            raise ValueError("Дата наблюдения не может быть в будущем")
        return v

    model_config = {
        "from_attributes": True
    }


class ObservationCreate(ObservationBase):
    """Схема для создания наблюдения"""
    pass


class ObservationUpdate(BaseModel):
    """Схема для обновления наблюдения"""

    location: Optional[str] = Field(None, max_length=200)
    equipment: Optional[str] = Field(None, max_length=200)
    duration_hours: Optional[float] = Field(None, ge=0)
    weather_conditions: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    data_collected: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class ObservationResponse(ObservationBase):
    """Схема для ответа"""

    id: int = Field(..., description="ID наблюдения")
    created_at: datetime = Field(..., description="Время создания записи")
    updated_at: datetime = Field(..., description="Время последнего обновления")

    # Дополнительная информация (вычисляемые свойства из модели)
    astronomer_name: Optional[str] = Field(
        None,
        description="Имя астронома"
    )

    celestial_body_name: Optional[str] = Field(
        None,
        description="Название небесного тела"
    )

    model_config = {
        "from_attributes": True
    }


    