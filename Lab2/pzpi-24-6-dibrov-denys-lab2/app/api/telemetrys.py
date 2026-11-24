from fastapi import APIRouter, Depends, Query, Response, status
from pydantic import AwareDatetime
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.crud import telemetry_measurement as measurement_crud
from app.crud import telemetry_session as telemetry_crud
from app.models.user import User
from app.schemas.telemetry_measurement import (
    TelemetryMeasurementCreate,
    TelemetryMeasurementResponse,
)
from app.schemas.telemetry_session import (
    TelemetrySessionCreate,
    TelemetrySessionEnd,
    TelemetrySessionResponse,
    TelemetrySessionUpdate,
)
from database import get_db


router = APIRouter(
    prefix="/telemetry/sessions",
    tags=["Telemetry"],
)


@router.post(
    "",
    response_model=TelemetrySessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_session(
    data: TelemetrySessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return telemetry_crud.create_telemetry_session(
        db,
        data,
        current_user,
    )


@router.get(
    "",
    response_model=list[TelemetrySessionResponse],
)
def list_sessions(
    service_session_id: int | None = Query(default=None, gt=0),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return telemetry_crud.get_telemetry_sessions(
        db,
        current_user,
        offset,
        limit,
        service_session_id,
    )


@router.get(
    "/{session_id}",
    response_model=TelemetrySessionResponse,
)
def read_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return telemetry_crud.get_telemetry_session(
        db,
        session_id,
        current_user,
    )


@router.patch(
    "/{session_id}",
    response_model=TelemetrySessionResponse,
)
def update_session(
    session_id: int,
    data: TelemetrySessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return telemetry_crud.update_telemetry_session(
        db,
        session_id,
        data,
        current_user,
    )


@router.post(
    "/{session_id}/end",
    response_model=TelemetrySessionResponse,
)
def end_session(
    session_id: int,
    data: TelemetrySessionEnd | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ended_at = data.ended_at if data is not None else None

    return telemetry_crud.end_telemetry_session(
        db,
        session_id,
        current_user,
        ended_at,
    )


@router.post(
    "/{session_id}/measurements",
    response_model=TelemetryMeasurementResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_measurement(
    session_id: int,
    data: TelemetryMeasurementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return measurement_crud.create_telemetry_measurement(
        db,
        session_id,
        data,
        current_user,
    )


@router.get(
    "/{session_id}/measurements",
    response_model=list[TelemetryMeasurementResponse],
)
def list_measurements(
    session_id: int,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    measured_from: AwareDatetime | None = Query(default=None),
    measured_to: AwareDatetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return measurement_crud.get_telemetry_measurements(
        db,
        session_id,
        current_user,
        offset,
        limit,
        measured_from,
        measured_to,
    )
    
    
    
@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    telemetry_crud.delete_telemetry_session(
        db,
        session_id,
        current_user,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )