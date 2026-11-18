from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.crud import component as component_crud
from app.models.user import User
from app.schemas.component import (
    ComponentCreate,
    ComponentResponse,
    ComponentUpdate,
)
from database import get_db


router = APIRouter(
    prefix="/drones/{drone_id}/components",
    tags=["Components"],
)


@router.post(
    "",
    response_model=ComponentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_component(
    drone_id: int,
    data: ComponentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return component_crud.create_component(
        db, drone_id, data, current_user
    )


@router.get(
    "",
    response_model=list[ComponentResponse],
)
def list_components(
    drone_id: int,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return component_crud.get_components(
        db, drone_id, current_user, offset, limit
    )


@router.get(
    "/{component_id}",
    response_model=ComponentResponse,
)
def read_component(
    drone_id: int,
    component_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return component_crud.get_component(
        db, drone_id, component_id, current_user
    )


@router.put(
    "/{component_id}",
    response_model=ComponentResponse,
)
def update_component(
    drone_id: int,
    component_id: int,
    data: ComponentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return component_crud.update_component(
        db, drone_id, component_id, data, current_user
    )


@router.delete(
    "/{component_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_component(
    drone_id: int,
    component_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    component_crud.delete_component(
        db, drone_id, component_id, current_user
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )