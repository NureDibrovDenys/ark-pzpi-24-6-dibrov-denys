from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.crud.telemetry_session import get_telemetry_session
from app.models.telemetry.telemetry_measurement import TelemetryMeasurement
from app.models.user import User
from app.schemas.telemetry_measurement import TelemetryMeasurementCreate


def create_telemetry_measurement(
    db: Session,
    session_id: int,
    data: TelemetryMeasurementCreate,
    current_user: User,
) -> TelemetryMeasurement:
    telemetry_session = get_telemetry_session(
        db,
        session_id,
        current_user,
        for_update=True,
    )

    if telemetry_session.ended_at is not None:
        raise HTTPException(
            status_code=409,
            detail="Не можна додати вимірювання до завершеної сесії",
        )

    measurement_data = data.model_dump()

    if measurement_data["measured_at"] is None:
        measurement_data["measured_at"] = datetime.now(timezone.utc)

    if measurement_data["measured_at"] < telemetry_session.started_at:
        raise HTTPException(
            status_code=422,
            detail=(
                "Час вимірювання не може бути раніше "
                "за початок сесії"
            ),
        )

    measurement = TelemetryMeasurement(
        **measurement_data,
        telemetry_session_id=session_id,
    )

    db.add(measurement)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(measurement)

    return measurement


def get_telemetry_measurements(
    db: Session,
    session_id: int,
    current_user: User,
    offset: int = 0,
    limit: int = 50,
    measured_from: datetime | None = None,
    measured_to: datetime | None = None,
) -> list[TelemetryMeasurement]:
    get_telemetry_session(db, session_id, current_user)

    if (
        measured_from is not None
        and measured_to is not None
        and measured_from > measured_to
    ):
        raise HTTPException(
            status_code=422,
            detail="Початок періоду не може бути пізніше за кінець",
        )

    statement = select(TelemetryMeasurement).where(
        TelemetryMeasurement.telemetry_session_id == session_id
    )

    if measured_from is not None:
        statement = statement.where(
            TelemetryMeasurement.measured_at >= measured_from
        )

    if measured_to is not None:
        statement = statement.where(
            TelemetryMeasurement.measured_at <= measured_to
        )

    statement = (
        statement
        .order_by(
            TelemetryMeasurement.measured_at,
            TelemetryMeasurement.id,
        )
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement).all())