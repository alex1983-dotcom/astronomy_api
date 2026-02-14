"""
Сервис для расширенного поиска и фильтрации.
"""

from sqlalchemy import select, and_
from sqlalchemy.sql.selectable import Select
from app.schemas.celestial_body import CelestialBodySearch
from app.models.celestial_body import CelestialBody


def apply_search_filters(query: Select, search_params: CelestialBodySearch) -> Select:
    """
    Применяет фильтры поиска к SQL запросу.

    **Параметры:**
    - `query`: базовый SQL запрос
    - `search_params`: параметры поиска

    **Возвращает:**
    - SQL запрос с примененными фильтрами
    """

    filters = []

    # Поиск по названию
    if search_params.name:
        filters.append(CelestialBody.name.ilike(f"%{search_params.name}%"))

    # Фильтр по типу
    if search_params.type:
        filters.append(CelestialBody.type == search_params.type)

    # Фильтр по расстоянию
    if search_params.min_distance is not None:
        filters.append(CelestialBody.distance_from_earth >= search_params.min_distance)

    if search_params.max_distance is not None:
        filters.append(CelestialBody.distance_from_earth <= search_params.max_distance)

    # Фильтр по звёздной величине
    if search_params.min_magnitude is not None:
        filters.append(CelestialBody.apparent_magnitude >= search_params.min_magnitude)

    if search_params.max_magnitude is not None:
        filters.append(CelestialBody.apparent_magnitude <= search_params.max_magnitude)

    # Фильтр по спектральному классу
    if search_params.spectral_class:
        filters.append(CelestialBody.spectral_class == search_params.spectral_class)

    # Фильтр по наличию наблюдений
    if search_params.has_observations is not None:
        if search_params.has_observations:
            # Тела с хотя бы одним наблюдением
            filters.append(CelestialBody.observations.any())
        else:
            # Тела без наблюдений
            filters.append(~CelestialBody.observations.any())

    # Применение всех фильтров
    if filters:
        query = query.where(and_(*filters))

    return query