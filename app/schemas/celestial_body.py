"""
Pydantic схемы для валидации данных небесных тел.

Используются для запросов и ответов API.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Перечисление для схемы (дублирует модель, но для валидации)
class BodyType(str, Enum):
    PLANET = "PLANET"
    STAR = "STAR"
    GALAXY = "GALAXY"
    NEBULA = "NEBULA"
    COMET = "COMET"
    ASTEROID = "ASTEROID"
    BLACK_HOLE = "BLACK_HOLE"


class SpectralClass(str, Enum):
    O = "O"
    B = "B"
    A = "A"
    F = "F"
    G = "G"
    K = "K"
    M = "M"


class CelestialBodyBase(BaseModel):
    """
    Базовая схема небесного тела.

    Содержит общие поля для создания и обновления.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Название небесного тела"
    )

    type: BodyType = Field(..., description="Тип небесного тела")

    description: Optional[str] = Field(
        None,
        description="Описание небесного тела"
    )

    mass: Optional[float] = Field(
        None,
        ge=0,
        description="Масса в массах Солнца/Земли"
    )

    radius: Optional[float] = Field(
        None,
        ge=0,
        description="Радиус в радиусах Солнца/Земли"
    )

    temperature: Optional[float] = Field(
        None,
        ge=0,
        description="Температура поверхности в Кельвинах"
    )

    distance_from_earth: Optional[float] = Field(
        None,
        ge=0,
        description="Расстояние от Земли в световых годах"
    )

    spectral_class: Optional[SpectralClass] = Field(
        None,
        description="Спектральный класс (только для звезд)"
    )

    absolute_magnitude: Optional[float] = Field(
        None,
        description="Абсолютная звёздная величина"
    )

    apparent_magnitude: Optional[float] = Field(
        None,
        description="Видимая звёздная величина"
    )

    right_ascension: Optional[float] = Field(
        None,
        ge=0,
        le=24,
        description="Прямое восхождение (0-24 часа)"
    )

    declination: Optional[float] = Field(
        None,
        ge=-90,
        le=90,
        description="Склонение (-90 до 90 градусов)"
    )

    parent_id: Optional[int] = Field(
        None,
        ge=1,
        description="ID родительского небесного тела"
    )

    # Валидатор для проверки логических ограничений
    @field_validator("spectral_class")
    @classmethod
    def validate_spectral_class(cls, v, info):
        """
        Валидатор спектрального класса.

        Проверяет, что спектральный класс указан только для звезд.
        """
        body_type = info.data.get("type")
        if v is not None and body_type != BodyType.STAR:
            raise ValueError("Спектральный класс может быть указан только для звезд")
        return v

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v):
        """Валидатор температуры"""
        if v is not None and v > 100000000:  # 100 миллионов К
            raise ValueError("Температура не может быть больше 100 миллионов К")
        return v

    model_config = {
        "from_attributes": True
    }


class CelestialBodyCreate(CelestialBodyBase):
    """
    Схема для создания небесного тела.

    Наследует все поля от CelestialBodyBase.
    """
    pass


class CelestialBodyUpdate(BaseModel):
    """
    Схема для обновления небесного тела.

    Все поля опциональны, так как можно обновить только часть данных.
    Не наследует от CelestialBodyBase, чтобы избежать конфликта типов.
    """

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Название небесного тела"
    )

    type: Optional[BodyType] = Field(None, description="Тип небесного тела")

    description: Optional[str] = Field(
        None,
        description="Описание небесного тела"
    )

    mass: Optional[float] = Field(
        None,
        ge=0,
        description="Масса в массах Солнца/Земли"
    )

    radius: Optional[float] = Field(
        None,
        ge=0,
        description="Радиус в радиусах Солнца/Земли"
    )

    temperature: Optional[float] = Field(
        None,
        ge=0,
        description="Температура поверхности в Кельвинах"
    )

    distance_from_earth: Optional[float] = Field(
        None,
        ge=0,
        description="Расстояние от Земли в световых годах"
    )

    spectral_class: Optional[SpectralClass] = Field(
        None,
        description="Спектральный класс (только для звезд)"
    )

    absolute_magnitude: Optional[float] = Field(
        None,
        description="Абсолютная звёздная величина"
    )

    apparent_magnitude: Optional[float] = Field(
        None,
        description="Видимая звёздная величина"
    )

    right_ascension: Optional[float] = Field(
        None,
        ge=0,
        le=24,
        description="Прямое восхождение (0-24 часа)"
    )

    declination: Optional[float] = Field(
        None,
        ge=-90,
        le=90,
        description="Склонение (-90 до 90 градусов)"
    )

    parent_id: Optional[int] = Field(
        None,
        ge=1,
        description="ID родительского небесного тела"
    )

    # Валидаторы остаются теми же
    @field_validator("spectral_class")
    @classmethod
    def validate_spectral_class(cls, v, info):
        """
        Валидатор спектрального класса.

        Проверяет, что спектральный класс указан только для звезд.
        """
        body_type = info.data.get("type")
        if v is not None and body_type != BodyType.STAR:
            raise ValueError("Спектральный класс может быть указан только для звезд")
        return v

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v):
        """Валидатор температуры"""
        if v is not None and v > 100000000:  # 100 миллионов К
            raise ValueError("Температура не может быть больше 100 миллионов К")
        return v

    model_config = {
        "from_attributes": True
    }


class CelestialBodyResponse(CelestialBodyBase):
    """
    Схема для ответа с полной информацией.

    Добавляет поля с метаданными и связанными данными.
    """

    id: int = Field(..., description="ID небесного тела")

    # Метаданные
    created_at: datetime = Field(..., description="Время создания записи")
    updated_at: datetime = Field(..., description="Время последнего обновления")

    # Связанные данные (вычисляемые свойства из модели)
    parent_name: Optional[str] = Field(
        None,
        description="Название родительского тела"
    )

    children_count: Optional[int] = Field(
        None,
        description="Количество дочерних тел"
    )

    observation_count: Optional[int] = Field(
        None,
        description="Количество наблюдений"
    )

    # Список астрономов
    observers: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Список астрономов, наблюдавших это тело"
    )

    model_config = {
        "from_attributes": True
    }


class CelestialBodySearch(BaseModel):
    """
    Схема для поиска небесных тел.

    Используется для фильтрации и поиска.
    """

    name: Optional[str] = Field(
        None,
        description="Поиск по названию (частичное совпадение)"
    )

    type: Optional[BodyType] = Field(
        None,
        description="Фильтр по типу"
    )

    min_distance: Optional[float] = Field(
        None,
        ge=0,
        description="Минимальное расстояние от Земли"
    )

    max_distance: Optional[float] = Field(
        None,
        ge=0,
        description="Максимальное расстояние от Земли"
    )

    min_magnitude: Optional[float] = Field(
        None,
        description="Минимальная видимая звёздная величина"
    )

    max_magnitude: Optional[float] = Field(
        None,
        description="Максимальная видимая звёздная величина"
    )

    spectral_class: Optional[SpectralClass] = Field(
        None,
        description="Фильтр по спектральному классу"
    )

    has_observations: Optional[bool] = Field(
        None,
        description="Только тела с наблюдениями"
    )

    @model_validator(mode='before')
    @classmethod
    def validate_distance_range(cls, values):
        """Проверка логичности диапазона расстояний"""
        min_d = values.get("min_distance")
        max_d = values.get("max_distance")
        if min_d is not None and max_d is not None and min_d > max_d:
            raise ValueError("Минимальное расстояние не может быть больше максимального")
        return values

    @model_validator(mode='before')
    @classmethod
    def validate_magnitude_range(cls, values):
        """Проверка логичности диапазона звёздных величин"""
        min_m = values.get("min_magnitude")
        max_m = values.get("max_magnitude")
        if min_m is not None and max_m is not None and min_m > max_m:
            raise ValueError("Минимальная величина не может быть больше максимальной")
        return values

    model_config = {
        "from_attributes": True
    }

    