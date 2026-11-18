from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.models.component import Component
from app.models.drone import Drone
from app.models.service_session import ServiceSession
from app.models.user import User
from app.schemas.drone import DroneCreate, DroneUpdate


def get_drone(
    db: Session,
    drone_id: int,
    current_user: User,
) -> Drone:
    drone = db.get(Drone, drone_id)

    if drone is None:
        raise HTTPException(
            status_code=404,
            detail="Дрон не знайдено",
        )

    if (
        current_user.role != UserRole.ADMIN
        and drone.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Немає доступу до цього дрона",
        )

    return drone


def get_drones(
    db: Session,
    current_user: User,
    offset: int = 0,
    limit: int = 50,
    serial_number: str | None = None,
) -> list[Drone]:
    statement = select(Drone)

    if current_user.role != UserRole.ADMIN:
        statement = statement.where(
            Drone.owner_id == current_user.id
        )

    if serial_number is not None:
        statement = statement.where(
            Drone.serial_number == serial_number.strip()
        )

    statement = (
        statement
        .order_by(Drone.id)
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def _save_drone(db: Session, drone: Drone) -> Drone:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()

        if getattr(exc.orig, "sqlstate", None) == "23505":
            raise HTTPException(
                status_code=409,
                detail="Дрон із таким серійним номером уже існує",
            ) from None

        raise

    db.refresh(drone)
    return drone


def create_drone(
    db: Session,
    data: DroneCreate,
    current_user: User,
) -> Drone:
    drone = Drone(
        **data.model_dump(),
        owner_id=current_user.id,
    )

    db.add(drone)
    return _save_drone(db, drone)


def update_drone(
    db: Session,
    drone_id: int,
    data: DroneUpdate,
    current_user: User,
) -> Drone:
    drone = get_drone(db, drone_id, current_user)

    for field, value in data.model_dump().items():
        setattr(drone, field, value)

    return _save_drone(db, drone)


def delete_drone(
    db: Session,
    drone_id: int,
    current_user: User,
) -> None:
    drone = get_drone(db, drone_id, current_user)

    has_components = db.scalar(
        select(Component.id)
        .where(Component.drone_id == drone.id)
        .limit(1)
    ) is not None

    has_service_sessions = db.scalar(
        select(ServiceSession.id)
        .where(ServiceSession.drone_id == drone.id)
        .limit(1)
    ) is not None

    if has_components or has_service_sessions:
        raise HTTPException(
            status_code=409,
            detail=(
                "Не можна видалити дрон, який має компоненти "
                "або історію обслуговування"
            ),
        )

    try:
        db.execute(
            delete(Drone).where(Drone.id == drone.id)
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()

        if getattr(exc.orig, "sqlstate", None) == "23503":
            raise HTTPException(
                status_code=409,
                detail="Дрон має пов’язані записи",
            ) from None

        raise