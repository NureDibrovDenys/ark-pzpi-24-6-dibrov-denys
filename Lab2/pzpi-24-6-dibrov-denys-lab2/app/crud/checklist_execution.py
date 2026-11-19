from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.core.enums import CheckListExecutionStatus
from app.crud.checklist import get_checklist
from app.crud.service_session import get_service_session
from app.models.checklists import (
    ChecklistAnswer,
    ChecklistExecution,
    ChecklistItem,
)
from app.models.user import User
from app.schemas.checklist_execution import (
    ChecklistAnswerSave,
    ChecklistExecutionCreate,
)


def _commit(db: Session) -> None:
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise


def get_execution(
    db: Session,
    drone_id: int,
    session_id: int,
    execution_id: int,
    current_user: User,
    for_update: bool = False,
) -> ChecklistExecution:
    get_service_session(
        db, drone_id, session_id, current_user
    )

    statement = (
        select(ChecklistExecution)
        .where(
            ChecklistExecution.id == execution_id,
            ChecklistExecution.service_session_id == session_id,
        )
        .options(
            selectinload(ChecklistExecution.answers)
        )
        .execution_options(populate_existing=True)
    )

    if for_update:
        statement = statement.with_for_update()

    execution = db.scalar(statement)

    if execution is None:
        raise HTTPException(
            status_code=404,
            detail="Проходження в цьому сервісному сеансі не знайдено",
        )

    return execution


def get_executions(
    db: Session,
    drone_id: int,
    session_id: int,
    current_user: User,
    offset: int = 0,
    limit: int = 50,
) -> list[ChecklistExecution]:
    get_service_session(
        db, drone_id, session_id, current_user
    )

    statement = (
        select(ChecklistExecution)
        .where(
            ChecklistExecution.service_session_id == session_id
        )
        .order_by(ChecklistExecution.id.desc())
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def create_execution(
    db: Session,
    drone_id: int,
    session_id: int,
    data: ChecklistExecutionCreate,
    current_user: User,
) -> ChecklistExecution:
    get_service_session(
        db, drone_id, session_id, current_user
    )

    checklist = get_checklist(
        db, data.checklist_id, for_update=True
    )

    if not checklist.items:
        raise HTTPException(
            status_code=409,
            detail="Не можна пройти шаблон без пунктів",
        )

    execution = ChecklistExecution(
        checklist_id=checklist.id,
        service_session_id=session_id,
        started_at=datetime.now(timezone.utc),
        status=CheckListExecutionStatus.IN_PROGRESS,
    )

    db.add(execution)
    _commit(db)

    return get_execution(
        db, drone_id, session_id, execution.id, current_user
    )


def _ensure_in_progress(
    execution: ChecklistExecution,
) -> None:
    if execution.status != CheckListExecutionStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=409,
            detail="Завершене проходження не можна змінювати",
        )


def save_answer(
    db: Session,
    drone_id: int,
    session_id: int,
    execution_id: int,
    item_id: int,
    data: ChecklistAnswerSave,
    current_user: User,
) -> ChecklistAnswer:
    execution = get_execution(
        db,
        drone_id,
        session_id,
        execution_id,
        current_user,
        for_update=True,
    )

    _ensure_in_progress(execution)

    item = db.scalar(
        select(ChecklistItem).where(
            ChecklistItem.id == item_id,
            ChecklistItem.checklist_id == execution.checklist_id,
        )
    )

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Пункт не належить шаблону цього проходження",
        )

    answer = db.scalar(
        select(ChecklistAnswer).where(
            ChecklistAnswer.execution_id == execution.id,
            ChecklistAnswer.checklist_items_id == item_id,
        )
    )

    if answer is None:
        answer = ChecklistAnswer(
            execution_id=execution.id,
            checklist_items_id=item_id,
            status=data.status,
            comment=data.comment,
        )
        db.add(answer)
    else:
        answer.status = data.status
        answer.comment = data.comment

    _commit(db)
    db.refresh(answer)

    return answer


def complete_execution(
    db: Session,
    drone_id: int,
    session_id: int,
    execution_id: int,
    current_user: User,
) -> ChecklistExecution:
    execution = get_execution(
        db,
        drone_id,
        session_id,
        execution_id,
        current_user,
        for_update=True,
    )

    _ensure_in_progress(execution)

    required_ids = set(
        db.scalars(
            select(ChecklistItem.id).where(
                ChecklistItem.checklist_id == execution.checklist_id,
                ChecklistItem.is_required.is_(True),
            )
        ).all()
    )

    answered_ids = {
        answer.checklist_items_id
        for answer in execution.answers
    }

    missing_ids = sorted(required_ids - answered_ids)

    if missing_ids:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Не заповнено всі обов’язкові пункти",
                "missing_item_ids": missing_ids,
            },
        )

    execution.status = CheckListExecutionStatus.COMPLETED
    execution.completed_at = datetime.now(timezone.utc)

    _commit(db)

    return get_execution(
        db, drone_id, session_id, execution_id, current_user
    )