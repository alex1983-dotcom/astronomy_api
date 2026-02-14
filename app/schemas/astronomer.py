"""
Pydantic схемы для астрономов.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime


class AstronomerBase(BaseModel):
    """
    Базовая схема астронома.
    """

    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Имя астронома"
    )

    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Фамилия астронома"
    )

    birth_date: Optional[date] = Field(
        None,
        description="Дата рождения"
    )

    death_date: Optional[date] = Field(
        None,
        description="Дата смерти"
    )

    nationality: Optional[str] = Field(
        None,
        max_length=100,
        description="Национальность"
    )

    biography: Optional[str] = Field(
        None,
        description="Биография"
    )

    achievements: Optional[str] = Field(
        None,
        description="Научные достижения"
    )

    notable_discoveries: Optional[str] = Field(
        None,
        description="Известные открытия"
    )

    academic_degree: Optional[str] = Field(
        None,
        max_length=100,
        description="Академическая степень"
    )

    institution: Optional[str] = Field(
        None,
        max_length=200,
        description="Место работы"
    )

    is_active: bool = Field(
        True,
        description="Активен ли астроном"
    )

    @field_validator("death_date")
    @classmethod
    def validate_death_date(cls, v, info):
        """Проверка, что дата смерти позже даты рождения"""
        birth = info.data.get("birth_date")
        if v and birth and v < birth:
            raise ValueError("Дата смерти не может быть раньше даты рождения")
        return v

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v):
        """Проверка, что дата рождения не в будущем"""
        if v and v > date.today():
            raise ValueError("Дата рождения не может быть в будущем")
        return v

    model_config = {
        "from_attributes": True
    }


class AstronomerCreate(AstronomerBase):
    """Схема для создания астронома"""
    pass


class AstronomerUpdate(BaseModel):
    """
    Схема для обновления астронома.
    
    Все поля опциональны, так как можно обновить только часть данных.
    Не наследует от AstronomerBase, чтобы избежать конфликта типов.
    """

    first_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Имя астронома"
    )

    last_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Фамилия астронома"
    )

    birth_date: Optional[date] = Field(
        None,
        description="Дата рождения"
    )

    death_date: Optional[date] = Field(
        None,
        description="Дата смерти"
    )

    nationality: Optional[str] = Field(
        None,
        max_length=100,
        description="Национальность"
    )

    biography: Optional[str] = Field(
        None,
        description="Биография"
    )

    achievements: Optional[str] = Field(
        None,
        description="Научные достижения"
    )

    notable_discoveries: Optional[str] = Field(
        None,
        description="Известные открытия"
    )

    academic_degree: Optional[str] = Field(
        None,
        max_length=100,
        description="Академическая степень"
    )

    institution: Optional[str] = Field(
        None,
        max_length=200,
        description="Место работы"
    )

    is_active: Optional[bool] = Field(
        None,
        description="Активен ли астроном"
    )

    @field_validator("death_date")
    @classmethod
    def validate_death_date(cls, v, info):
        """Проверка, что дата смерти позже даты рождения"""
        birth = info.data.get("birth_date")
        if v and birth and v < birth:
            raise ValueError("Дата смерти не может быть раньше даты рождения")
        return v

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v):
        """Проверка, что дата рождения не в будущем"""
        if v and v > date.today():
            raise ValueError("Дата рождения не может быть в будущем")
        return v

    model_config = {
        "from_attributes": True
    }


class AstronomerResponse(AstronomerBase):
    """Схема для ответа"""

    id: int = Field(..., description="ID астронома")
    created_at: datetime = Field(..., description="Время создания записи")
    updated_at: datetime = Field(..., description="Время последнего обновления")

    # Статистика (вычисляемые свойства из модели)
    observation_count: Optional[int] = Field(
        None,
        description="Количество наблюдений"
    )

    observed_bodies_count: Optional[int] = Field(
        None,
        description="Количество наблюдавшихся тел"
    )

    # Список наблюдавшихся тел
    observed_bodies: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Список небесных тел, которые наблюдал астроном"
    )

    model_config = {
        "from_attributes": True
    }


class AstronomerSearch(BaseModel):
    """Схема для поиска астрономов"""

    name: Optional[str] = Field(
        None,
        description="Поиск по имени или фамилии"
    )

    nationality: Optional[str] = Field(
        None,
        description="Фильтр по национальности"
    )

    institution: Optional[str] = Field(
        None,
        description="Фильтр по месту работы"
    )

    is_active: Optional[bool] = Field(
        None,
        description="Фильтр по активности"
    )

    has_observations: Optional[bool] = Field(
        None,
        description="Только астрономы с наблюдениями"
    )

    model_config = {
        "from_attributes": True
    }

    