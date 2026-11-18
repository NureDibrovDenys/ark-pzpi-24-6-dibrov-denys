from fastapi import HTTPException
from sqlalchemy import delete, or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.crud.drone import get_drone
from app.models.service_session import ServiceSession
from app.models.user import User
from app.schemas.service_session import (
    ServiceSessionCreate,
    ServiceSessionUpdate,
)


def get_service_session(
    db: Session,
    drone_id: int,
    session_id: int,
    current_user: User,
) -> ServiceSession:
    get_drone(db, drone_id, current_user)

    service_session = db.scalar(
        select(ServiceSession).where(
            ServiceSession.id == session_id,
            ServiceSession.drone_id == drone_id,
        )
    )

    if service_session is None:
        raise HTTPException(
            status_code=404,
            detail="Сервісний сеанс у цьому дроні не знайдено",
        )

    return service_session


def get_service_sessions(
    db: Session,
    drone_id: int,
    current_user: User,
    offset: int = 0,
    limit: int = 50,
) -> list[ServiceSession]:
    get_drone(db, drone_id, current_user)

    statement = (
        select(ServiceSession)
        .where(ServiceSession.drone_id == drone_id)
        .order_by(
            ServiceSession.started_at.desc(),
            ServiceSession.id.desc(),
        )
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def _save_service_session(
    db: Session,
    service_session: ServiceSession,
) -> ServiceSession:
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(service_session)
    return service_session


def create_service_session(
    db: Session,
    drone_id: int,
    data: ServiceSessionCreate,
    current_user: User,
) -> ServiceSession:
    get_drone(db, drone_id, current_user)

    service_session = ServiceSession(
        **data.model_dump(),
        drone_id=drone_id,
    )

    db.add(service_session)

    return _save_service_session(db, service_session)


def update_service_session(
    db: Session,
    drone_id: int,
    session_id: int,
    data: ServiceSessionUpdate,
    current_user: User,
) -> ServiceSession:
    service_session = get_service_session(
        db, drone_id, session_id, current_user
    )

    for field, value in data.model_dump().items():
        setattr(service_session, field, value)

    return _save_service_session(db, service_session)


def delete_service_session(
    db: Session,
    drone_id: int,
    session_id: int,
    current_user: User,
) -> None:
    service_session = get_service_session(
        db, drone_id, session_id, current_user
    )

    has_related_records = db.scalar(
        select(ServiceSession.id)
        .where(
            ServiceSession.id == service_session.id,
            or_(
                ServiceSession.checklist_executions.any(),
                ServiceSession.photos.any(),
                ServiceSession.telemetry_sessions.any(),
            ),
        )
        .limit(1)
    ) is not None

    if has_related_records:
        raise HTTPException(
            status_code=409,
            detail=(
                "Не можна видалити сервісний сеанс, "
                "який має чеклісти, фото або телеметрію"
            ),
        )

    try:
        db.execute(
            delete(ServiceSession).where(
                ServiceSession.id == service_session.id
            )
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()

        if getattr(exc.orig, "sqlstate", None) == "23503":
            raise HTTPException(
                status_code=409,
                detail="Сервісний сеанс має пов’язані записи",
            ) from None

        raise
    except SQLAlchemyError:
        db.rollback()
        raise