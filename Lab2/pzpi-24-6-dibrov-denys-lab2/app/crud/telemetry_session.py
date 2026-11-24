from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.crud.drone import get_drone
from app.models.drone import Drone
from app.models.service_session import ServiceSession
from app.models.telemetry.telemetry_measurement import TelemetryMeasurement
from app.models.telemetry.telemetry_session import TelemetrySession
from app.models.user import User
from app.schemas.telemetry_session import (
    TelemetrySessionCreate,
    TelemetrySessionUpdate,
)


def _get_service_session(
    db: Session,
    service_session_id: int,
    current_user: User,
) -> ServiceSession:
    service_session = db.get(ServiceSession, service_session_id)

    if service_session is None:
        raise HTTPException(
            status_code=404,
            detail="Сервісний сеанс не знайдено",
        )

    get_drone(db, service_session.drone_id, current_user)

    return service_session


def create_telemetry_session(
    db: Session,
    data: TelemetrySessionCreate,
    current_user: User,
) -> TelemetrySession:
    _get_service_session(db, data.service_session_id, current_user)

    session_data = data.model_dump()

    if session_data["started_at"] is None:
        session_data["started_at"] = datetime.now(timezone.utc)

    telemetry_session = TelemetrySession(**session_data)

    db.add(telemetry_session)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(telemetry_session)

    return telemetry_session


def get_telemetry_sessions(
    db: Session,
    current_user: User,
    offset: int = 0,
    limit: int = 50,
    service_session_id: int | None = None,
) -> list[TelemetrySession]:
    statement = (
        select(TelemetrySession)
        .join(
            ServiceSession,
            TelemetrySession.service_session_id == ServiceSession.id,
        )
        .join(
            Drone,
            ServiceSession.drone_id == Drone.id,
        )
    )

    if current_user.role != UserRole.ADMIN:
        statement = statement.where(
            Drone.owner_id == current_user.id
        )

    if service_session_id is not None:
        _get_service_session(db, service_session_id, current_user)

        statement = statement.where(
            TelemetrySession.service_session_id == service_session_id
        )

    statement = (
        statement
        .order_by(TelemetrySession.id.desc())
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def get_telemetry_session(
    db: Session,
    session_id: int,
    current_user: User,
    for_update: bool = False,
) -> TelemetrySession:
    statement = select(TelemetrySession).where(
        TelemetrySession.id == session_id
    )

    # Для запису вимірювання та завершення блокуємо рядок сесії.
    if for_update:
        statement = statement.with_for_update()

    telemetry_session = db.scalar(statement)

    if telemetry_session is None:
        raise HTTPException(
            status_code=404,
            detail="Сесію телеметрії не знайдено",
        )

    _get_service_session(
        db,
        telemetry_session.service_session_id,
        current_user,
    )

    return telemetry_session


def update_telemetry_session(
    db: Session,
    session_id: int,
    data: TelemetrySessionUpdate,
    current_user: User,
) -> TelemetrySession:
    telemetry_session = get_telemetry_session(
        db,
        session_id,
        current_user,
        for_update=True,
    )

    # Змінюємо опис лише тоді, коли поле передали в запиті.
    if "description" in data.model_fields_set:
        telemetry_session.description = data.description

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(telemetry_session)

    return telemetry_session


def end_telemetry_session(
    db: Session,
    session_id: int,
    current_user: User,
    ended_at: datetime | None = None,
) -> TelemetrySession:
    telemetry_session = get_telemetry_session(
        db,
        session_id,
        current_user,
        for_update=True,
    )

    if telemetry_session.ended_at is not None:
        raise HTTPException(
            status_code=409,
            detail="Сесію телеметрії вже завершено",
        )

    if ended_at is None:
        ended_at = datetime.now(timezone.utc)

    if ended_at.tzinfo is None or ended_at.utcoffset() is None:
        raise HTTPException(
            status_code=422,
            detail="Час завершення повинен містити часовий пояс",
        )

    if ended_at < telemetry_session.started_at:
        raise HTTPException(
            status_code=422,
            detail="Час завершення не може бути раніше за час початку",
        )

    last_measured_at = db.scalar(
        select(func.max(TelemetryMeasurement.measured_at)).where(
            TelemetryMeasurement.telemetry_session_id == session_id
        )
    )

    if last_measured_at is not None and ended_at < last_measured_at:
        raise HTTPException(
            status_code=422,
            detail=(
                "Час завершення не може бути раніше "
                "за останнє вимірювання"
            ),
        )

    telemetry_session.ended_at = ended_at

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(telemetry_session)

    return telemetry_session