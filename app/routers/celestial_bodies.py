"""
Маршрут для работы с небесными телами.

Содержит все CRUD операции и дополнительные методы.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional

from app.database import get_db
from app.models.celestial_body import CelestialBody, BodyType, SpectralClass
from app.schemas.celestial_body import (
    CelestialBodyCreate,
    CelestialBodyUpdate,
    CelestialBodyResponse,
    CelestialBodySearch
)
from app.services.search import apply_search_filters


router = APIRouter(
    prefix="/celestial-bodies",
    tags=["Небесные тела"],
    responses={404: {"description": "Не найдено"}}
)


# ========== CRUD операции ==========

@router.post(
    "/",
    response_model=CelestialBodyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать небесное тело",
    description="Создает новую запись о небесном теле в базе данных"
)
async def create_celestial_body(
    body: CelestialBodyCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Создание нового небесного тела.

    **Параметры:**
    - `body`: данные о небесном теле

    **Возвращает:**
    - Созданное небесное тело с полной информацией
    """

    # Проверка существования тела с таким именем
    query = select(CelestialBody).where(CelestialBody.name == body.name)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Небесное тело с именем '{body.name}' уже существует"
        )

    # Проверка существования родительского тела
    if body.parent_id:
        parent_query = select(CelestialBody).where(CelestialBody.id == body.parent_id)
        parent_result = await db.execute(parent_query)
        parent = parent_result.scalar_one_or_none()

        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Родительское тело с ID {body.parent_id} не найдено"
            )

    # Создание нового объекта
    db_body = CelestialBody(**body.model_dump())

    # Добавление в сессию
    db.add(db_body)

    # Фиксация изменений
    await db.commit()

    # Обновление объекта
    await db.refresh(db_body)

    return db_body


@router.get(
    "/",
    response_model=List[CelestialBodyResponse],
    summary="Получить список небесных тел",
    description="Возвращает список небесных тел с пагинацией и фильтрацией"
)
async def read_celestial_bodies(
    skip: int = Query(0, ge=0, description="Количество пропущенных записей"),
    limit: int = Query(10, ge=1, le=100, description="Количество записей"),
    search: Optional[str] = Query(None, description="Поиск по названию"),
    body_type: Optional[BodyType] = Query(None, description="Фильтр по типу"),
    min_distance: Optional[float] = Query(None, ge=0, description="Минимальное расстояние"),
    max_distance: Optional[float] = Query(None, ge=0, description="Максимальное расстояние"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение списка небесных тел с возможностью фильтрации.

    **Параметры:**
    - `skip`: количество пропущенных записей (для пагинации)
    - `limit`: количество записей на страницу
    - `search`: поиск по названию
    - `body_type`: фильтр по типу тела
    - `min_distance`, `max_distance`: фильтр по расстоянию

    **Возвращает:**
    - Список небесных тел
    """

    # Создание базового запроса
    query = select(CelestialBody)

    # Применение фильтров
    if search:
        query = query.where(CelestialBody.name.ilike(f"%{search}%"))

    if body_type:
        query = query.where(CelestialBody.type == body_type)

    if min_distance is not None:
        query = query.where(CelestialBody.distance_from_earth >= min_distance)

    if max_distance is not None:
        query = query.where(CelestialBody.distance_from_earth <= max_distance)

    # Применение пагинации
    query = query.offset(skip).limit(limit)

    # Выполнение запроса
    result = await db.execute(query)
    bodies = result.scalars().all()

    return bodies


@router.get(
    "/{body_id}",
    response_model=CelestialBodyResponse,
    summary="Получить небесное тело по ID",
    description="Возвращает подробную информацию о небесном теле"
)
async def read_celestial_body(
    body_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Получение небесного тела по ID.

    **Параметры:**
    - `body_id`: ID небесного тела

    **Возвращает:**
    - Подробная информация о небесном теле
    """

    # Получение тела по ID
    query = select(CelestialBody).where(CelestialBody.id == body_id)
    result = await db.execute(query)
    body = result.scalar_one_or_none()

    if not body:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Небесное тело с ID {body_id} не найдено"
        )

    return body


@router.put(
    "/{body_id}",
    response_model=CelestialBodyResponse,
    summary="Обновить небесное тело",
    description="Обновляет информацию о небесном теле"
)
async def update_celestial_body(
    body_id: int,
    body_update: CelestialBodyUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление небесного тела.

    **Параметры:**
    - `body_id`: ID небесного тела
    - `body_update`: данные для обновления

    **Возвращает:**
    - Обновленное небесное тело
    """

    # Получение существующего тела
    query = select(CelestialBody).where(CelestialBody.id == body_id)
    result = await db.execute(query)
    db_body = result.scalar_one_or_none()

    if not db_body:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Небесное тело с ID {body_id} не найдено"
        )

    # Обновление полей
    update_data = body_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_body, field, value)

    await db.commit()
    await db.refresh(db_body)

    return db_body


@router.delete(
    "/{body_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить небесное тело",
    description="Удаляет небесное тело из базы данных"
)
async def delete_celestial_body(
    body_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Удаление небесного тела.

    **Параметры:**
    - `body_id`: ID небесного тела

    **Возвращает:**
    - 204 No Content при успешном удалении
    """

    query = select(CelestialBody).where(CelestialBody.id == body_id)
    result = await db.execute(query)
    db_body = result.scalar_one_or_none()

    if not db_body:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Небесное тело с ID {body_id} не найдено"
        )

    # Удаление объекта
    await db.delete(db_body)
    await db.commit()

    return None


# ========== Расширенные методы ==========

@router.get(
    "/search/advanced",
    response_model=List[CelestialBodyResponse],
    summary="Расширенный поиск небесных тел",
    description="Поиск с множеством фильтров и сортировкой"
)
async def search_celestial_bodies(
    search_params: CelestialBodySearch = Depends(),
    sort_by: Optional[str] = Query(None, description="Поле для сортировки"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Порядок сортировки"),
    db: AsyncSession = Depends(get_db)
):
    """
    Расширенный поиск небесных тел.

    **Параметры:**
    - `search_params`: параметры поиска (через query параметры)
    - `sort_by`: поле для сортировки
    - `sort_order`: порядок сортировки (asc или desc)

    **Возвращает:**
    - Отфильтрованный и отсортированный список небесных тел
    """

    # Создание запроса
    query = select(CelestialBody)

    # Применение фильтров через сервис
    query = apply_search_filters(query, search_params)

    # Применение сортировки
    if sort_by:
        sort_column = getattr(CelestialBody, sort_by, None)
        if sort_column is not None:
            if sort_order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

    result = await db.execute(query)
    bodies = result.scalars().all()

    return bodies


@router.get(
    "/statistics",
    summary="Статистика по небесным телам",
    description="Возвращает статистику по типам небесных тел"
)
async def get_statistics(db: AsyncSession = Depends(get_db)):
    """
    Получение статистики по небесным телам.

    **Возвращает:**
    - Количество тел по типам
    - Общее количество
    - Статистика по расстояниям
    """

    # Подсчет количества по типам
    query = (
        select(CelestialBody.type, func.count(CelestialBody.id))
        .group_by(CelestialBody.type)
    )

    result = await db.execute(query)
    type_counts = {type_.value: count for type_, count in result.all()}

    # Общее количество
    total_query = select(func.count(CelestialBody.id))
    total_result = await db.execute(total_query)
    total = total_result.scalar()

    # Статистика по расстояниям
    distance_query = select(
        func.avg(CelestialBody.distance_from_earth),
        func.min(CelestialBody.distance_from_earth),
        func.max(CelestialBody.distance_from_earth)
    ).where(CelestialBody.distance_from_earth.isnot(None))

    distance_result = await db.execute(distance_query)
    result = distance_result.first()
    
    # Проверка на случай, если нет данных с расстояниями
    if result is None:
        avg_dist = min_dist = max_dist = None
    else:
        avg_dist, min_dist, max_dist = result

    return {
        "total": total,
        "by_type": type_counts,
        "distance_statistics": {
            "average": avg_dist,
            "minimum": min_dist,
            "maximum": max_dist
        }
    }


@router.get(
    "/{body_id}/children",
    response_model=List[CelestialBodyResponse],
    summary="Получить дочерние тела",
    description="Возвращает все дочерние небесные тела (спутники, планеты и т.д.)"
)
async def get_children(
    body_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Получение дочерних небесных тел.

    **Параметры:**
    - `body_id`: ID родительского тела

    **Возвращает:**
    - Список дочерних тел
    """

    query = select(CelestialBody).where(CelestialBody.parent_id == body_id)
    result = await db.execute(query)
    children = result.scalars().all()

    if not children:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Небесное тело с ID {body_id} не имеет дочерних тел или не существует"
        )

    return children


@router.get(
    "/{body_id}/observers",
    summary="Получить астрономов, наблюдавших тело",
    description="Возвращает список астрономов, которые наблюдали данное небесное тело"
)
async def get_observers(
    body_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Получение списка астрономов, наблюдавших тело.

    **Параметры:**
    - `body_id`: ID небесного тела

    **Возвращает:**
    - Список астрономов с информацией о наблюдениях
    """

    query = select(CelestialBody).where(CelestialBody.id == body_id)
    result = await db.execute(query)
    body = result.scalar_one_or_none()

    if not body:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Небесное тело с ID {body_id} не найдено"
        )

    # Загрузка астрономов через связь
    await db.refresh(body, ["observers"])

    observers_data = []
    for observer in body.observers:
        # Подсчет наблюдений этого астронома за данным телом
        obs_count = sum(
            1 for obs in observer.observations
            if obs.celestial_body_id == body_id
        )
        
        observers_data.append({
            "id": observer.id,
            "name": observer.full_name,
            "institution": observer.institution,
            "observation_count": obs_count
        })

    return {
        "celestial_body": body.name,
        "observer_count": len(body.observers),
        "observers": observers_data
    }


@router.post(
    "/batch",
    response_model=List[CelestialBodyResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Создать несколько небесных тел",
    description="Создает несколько небесных тел за один запрос"
)
async def create_batch_bodies(
    bodies: List[CelestialBodyCreate],
    db: AsyncSession = Depends(get_db)
):
    """
    Пакетное создание небесных тел.

    **Параметры:**
    - `bodies`: список небесных тел для создания

    **Возвращает:**
    - Список созданных небесных тел
    """

    created_bodies = []

    for body_data in bodies:
        # Проверка существования
        query = select(CelestialBody).where(CelestialBody.name == body_data.name)
        result = await db.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            continue  # Пропускаем существующие

        # Создание нового тела
        db_body = CelestialBody(**body_data.model_dump())
        db.add(db_body)
        created_bodies.append(db_body)

    await db.commit()

    # Обновление всех созданных объектов
    for body in created_bodies:
        await db.refresh(body)

    return created_bodies