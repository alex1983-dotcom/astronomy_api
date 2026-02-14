"""
Маршрут для работы с астрономами.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional

from app.database import get_db
from app.models.astronomer import Astronomer
from app.schemas.astronomer import (
    AstronomerCreate,
    AstronomerUpdate,
    AstronomerResponse,
    AstronomerSearch
)


router = APIRouter(
    prefix="/astronomers",
    tags=["Астрономы"],
    responses={404: {"description": "Не найдено"}}
)


@router.post(
    "/",
    response_model=AstronomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать астронома",
    description="Создает новую запись об астрономе"
)
async def create_astronomer(
    astronomer: AstronomerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создание нового астронома"""

    # Проверка существования
    query = select(Astronomer).where(
        (Astronomer.first_name == astronomer.first_name) &
        (Astronomer.last_name == astronomer.last_name)
    )
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Астроном {astronomer.first_name} {astronomer.last_name} уже существует"
        )

    db_astronomer = Astronomer(**astronomer.model_dump())
    db.add(db_astronomer)
    await db.commit()
    await db.refresh(db_astronomer)

    return db_astronomer


@router.get(
    "/",
    response_model=List[AstronomerResponse],
    summary="Получить список астрономов"
)
async def read_astronomers(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка астрономов"""

    query = select(Astronomer)

    if search:
        query = query.where(
            or_(
                Astronomer.first_name.ilike(f"%{search}%"),
                Astronomer.last_name.ilike(f"%{search}%")
            )
        )

    if is_active is not None:
        query = query.where(Astronomer.is_active == is_active)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    astronomers = result.scalars().all()

    return astronomers


@router.get(
    "/{astronomer_id}",
    response_model=AstronomerResponse,
    summary="Получить астронома по ID"
)
async def read_astronomer(
    astronomer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение астронома по ID"""

    query = select(Astronomer).where(Astronomer.id == astronomer_id)
    result = await db.execute(query)
    astronomer = result.scalar_one_or_none()

    if not astronomer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Астроном с ID {astronomer_id} не найден"
        )

    return astronomer


@router.put(
    "/{astronomer_id}",
    response_model=AstronomerResponse,
    summary="Обновить астронома"
)
async def update_astronomer(
    astronomer_id: int,
    astronomer_update: AstronomerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновление астронома"""

    query = select(Astronomer).where(Astronomer.id == astronomer_id)
    result = await db.execute(query)
    db_astronomer = result.scalar_one_or_none()

    if not db_astronomer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Астроном с ID {astronomer_id} не найден"
        )

    update_data = astronomer_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_astronomer, field, value)

    await db.commit()
    await db.refresh(db_astronomer)

    return db_astronomer


@router.delete(
    "/{astronomer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить астронома"
)
async def delete_astronomer(
    astronomer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление астронома"""

    query = select(Astronomer).where(Astronomer.id == astronomer_id)
    result = await db.execute(query)
    db_astronomer = result.scalar_one_or_none()

    if not db_astronomer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Астроном с ID {astronomer_id} не найден"
        )

    await db.delete(db_astronomer)
    await db.commit()

    return None


@router.get(
    "/statistics",
    summary="Статистика по астрономам"
)
async def get_astronomer_statistics(db: AsyncSession = Depends(get_db)):
    """Получение статистики по астрономам"""

    # Общее количество
    total_query = select(func.count(Astronomer.id))
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0  # Обработка None

    # Количество активных
    active_query = select(func.count(Astronomer.id)).where(Astronomer.is_active == True)
    active_result = await db.execute(active_query)
    active = active_result.scalar() or 0  # Обработка None

    # Статистика по национальностям
    nationality_query = (
        select(Astronomer.nationality, func.count(Astronomer.id))
        .where(Astronomer.nationality.isnot(None))
        .group_by(Astronomer.nationality)
        .order_by(func.count(Astronomer.id).desc())
    )
    nationality_result = await db.execute(nationality_query)
    nationalities = {nat: count for nat, count in nationality_result.all()}

    return {
        "total": total,
        "active": active,
        "inactive": total - active,  # Теперь безопасно
        "by_nationality": nationalities
    }

@router.get(
    "/{astronomer_id}/observations",
    summary="Получить наблюдения астронома"
)
async def get_astronomer_observations(
    astronomer_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Получение наблюдений конкретного астронома"""

    query = select(Astronomer).where(Astronomer.id == astronomer_id)
    result = await db.execute(query)
    astronomer = result.scalar_one_or_none()

    if not astronomer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Астроном с ID {astronomer_id} не найден"
        )

    await db.refresh(astronomer, ["observations"])

    observations_list = []
    for obs in astronomer.observations:
        observations_list.append({
            "id": obs.id,
            "celestial_body": obs.celestial_body.name if obs.celestial_body else None,
            "observation_date": obs.observation_date.isoformat(),
            "location": obs.location,
            "duration_hours": obs.duration_hours
        })

    return {
        "astronomer": astronomer.full_name,
        "observation_count": len(astronomer.observations),
        "observations": observations_list[skip:skip+limit]
    }