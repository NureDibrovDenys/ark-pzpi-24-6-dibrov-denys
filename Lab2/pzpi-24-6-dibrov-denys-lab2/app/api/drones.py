from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.crud import drone as drone_crud
from app.models.user import User
from app.schemas.drone import (
    DroneCreate,
    DroneResponse,
    DroneUpdate,
)
from database import get_db


router = APIRouter(
    prefix="/drones",
    tags=["Drones"],
)


@router.post(
    "",
    response_model=DroneResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_drone(
    data: DroneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return drone_crud.create_drone(
        db, data, current_user
    )


@router.get(
    "",
    response_model=list[DroneResponse],
)
def list_drones(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    serial_number: str | None = Query(
        default=None,
        min_length=1,
        max_length=255,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return drone_crud.get_drones(
        db=db,
        current_user=current_user,
        offset=offset,
        limit=limit,
        serial_number=serial_number,
    )


@router.get(
    "/{drone_id}",
    response_model=DroneResponse,
)
def read_drone(
    drone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return drone_crud.get_drone(
        db, drone_id, current_user
    )


@router.put(
    "/{drone_id}",
    response_model=DroneResponse,
)
def update_drone(
    drone_id: int,
    data: DroneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return drone_crud.update_drone(
        db, drone_id, data, current_user
    )


@router.delete(
    "/{drone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_drone(
    drone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    drone_crud.delete_drone(
        db, drone_id, current_user
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )