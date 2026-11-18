from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.crud import service_session as service_crud
from app.models.user import User
from app.schemas.service_session import (
    ServiceSessionCreate,
    ServiceSessionResponse,
    ServiceSessionUpdate,
)
from database import get_db


router = APIRouter(
    prefix="/drones/{drone_id}/service-sessions",
    tags=["Service sessions"],
)


@router.post(
    "",
    response_model=ServiceSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_service_session(
    drone_id: int,
    data: ServiceSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service_crud.create_service_session(
        db, drone_id, data, current_user
    )


@router.get(
    "",
    response_model=list[ServiceSessionResponse],
)
def list_service_sessions(
    drone_id: int,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service_crud.get_service_sessions(
        db, drone_id, current_user, offset, limit
    )


@router.get(
    "/{session_id}",
    response_model=ServiceSessionResponse,
)
def read_service_session(
    drone_id: int,
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service_crud.get_service_session(
        db, drone_id, session_id, current_user
    )


@router.put(
    "/{session_id}",
    response_model=ServiceSessionResponse,
)
def update_service_session(
    drone_id: int,
    session_id: int,
    data: ServiceSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service_crud.update_service_session(
        db, drone_id, session_id, data, current_user
    )


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_service_session(
    drone_id: int,
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service_crud.delete_service_session(
        db, drone_id, session_id, current_user
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )