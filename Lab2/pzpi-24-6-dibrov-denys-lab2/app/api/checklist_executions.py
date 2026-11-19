from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.crud import checklist_execution as execution_crud
from app.models.user import User
from app.schemas.checklist_execution import (
    ChecklistAnswerResponse,
    ChecklistAnswerSave,
    ChecklistExecutionCreate,
    ChecklistExecutionResponse,
    ChecklistExecutionSummary,
)
from database import get_db


router = APIRouter(
    prefix=(
        "/drones/{drone_id}"
        "/service-sessions/{session_id}"
        "/checklist-executions"
    ),
    tags=["Checklist executions"],
)


@router.post(
    "",
    response_model=ChecklistExecutionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_execution(
    drone_id: int,
    session_id: int,
    data: ChecklistExecutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return execution_crud.create_execution(
        db, drone_id, session_id, data, current_user
    )


@router.get(
    "",
    response_model=list[ChecklistExecutionSummary],
)
def list_executions(
    drone_id: int,
    session_id: int,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return execution_crud.get_executions(
        db, drone_id, session_id, current_user, offset, limit
    )


@router.get(
    "/{execution_id}",
    response_model=ChecklistExecutionResponse,
)
def read_execution(
    drone_id: int,
    session_id: int,
    execution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return execution_crud.get_execution(
        db, drone_id, session_id, execution_id, current_user
    )


@router.put(
    "/{execution_id}/answers/{item_id}",
    response_model=ChecklistAnswerResponse,
)
def save_answer(
    drone_id: int,
    session_id: int,
    execution_id: int,
    item_id: int,
    data: ChecklistAnswerSave,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return execution_crud.save_answer(
        db,
        drone_id,
        session_id,
        execution_id,
        item_id,
        data,
        current_user,
    )


@router.post(
    "/{execution_id}/complete",
    response_model=ChecklistExecutionResponse,
)
def complete_execution(
    drone_id: int,
    session_id: int,
    execution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return execution_crud.complete_execution(
        db, drone_id, session_id, execution_id, current_user
    )