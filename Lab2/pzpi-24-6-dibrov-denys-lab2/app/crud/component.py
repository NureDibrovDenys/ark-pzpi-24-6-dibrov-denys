from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.crud.drone import get_drone
from app.models.component import Component
from app.models.user import User
from app.schemas.component import (
    ComponentCreate,
    ComponentUpdate,
)


def get_component(
    db: Session,
    drone_id: int,
    component_id: int,
    current_user: User,
) -> Component:
    get_drone(db, drone_id, current_user)

    component = db.scalar(
        select(Component).where(
            Component.id == component_id,
            Component.drone_id == drone_id,
        )
    )

    if component is None:
        raise HTTPException(
            status_code=404,
            detail="Компонент у цьому дроні не знайдено",
        )

    return component


def get_components(
    db: Session,
    drone_id: int,
    current_user: User,
    offset: int = 0,
    limit: int = 50,
) -> list[Component]:
    get_drone(db, drone_id, current_user)

    statement = (
        select(Component)
        .where(Component.drone_id == drone_id)
        .order_by(Component.id)
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def _save_component(
    db: Session,
    component: Component,
) -> Component:
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(component)
    return component


def create_component(
    db: Session,
    drone_id: int,
    data: ComponentCreate,
    current_user: User,
) -> Component:
    get_drone(db, drone_id, current_user)

    component = Component(
        **data.model_dump(),
        drone_id=drone_id,
    )

    db.add(component)
    return _save_component(db, component)


def update_component(
    db: Session,
    drone_id: int,
    component_id: int,
    data: ComponentUpdate,
    current_user: User,
) -> Component:
    component = get_component(
        db, drone_id, component_id, current_user
    )

    for field, value in data.model_dump().items():
        setattr(component, field, value)

    return _save_component(db, component)


def delete_component(
    db: Session,
    drone_id: int,
    component_id: int,
    current_user: User,
) -> None:
    component = get_component(
        db, drone_id, component_id, current_user
    )

    try:
        db.delete(component)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise