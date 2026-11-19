from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_admin
from app.crud import checklist as checklist_crud
from app.models.user import User
from app.schemas.checklist import (
    ChecklistCreate,
    ChecklistResponse,
    ChecklistUpdate,
)
from database import get_db


router = APIRouter(
    prefix="/checklists",
    tags=["Checklist templates"],
)


@router.post(
    "",
    response_model=ChecklistResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_checklist(
    data: ChecklistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return checklist_crud.create_checklist(db, data)


@router.get(
    "",
    response_model=list[ChecklistResponse],
)
def list_checklists(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return checklist_crud.get_checklists(
        db, offset, limit
    )


@router.get(
    "/{checklist_id}",
    response_model=ChecklistResponse,
)
def read_checklist(
    checklist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return checklist_crud.get_checklist(
        db, checklist_id
    )


@router.put(
    "/{checklist_id}",
    response_model=ChecklistResponse,
)
def update_checklist(
    checklist_id: int,
    data: ChecklistUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return checklist_crud.update_checklist(
        db, checklist_id, data
    )


@router.delete(
    "/{checklist_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_checklist(
    checklist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    checklist_crud.delete_checklist(
        db, checklist_id
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )