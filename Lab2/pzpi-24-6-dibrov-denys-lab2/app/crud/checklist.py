from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.models.checklists import (
    Checklist,
    ChecklistExecution,
    ChecklistItem,
)
from app.schemas.checklist import (
    ChecklistCreate,
    ChecklistUpdate,
)


def get_checklist(
    db: Session,
    checklist_id: int,
    for_update: bool = False,
) -> Checklist:
    statement = (
        select(Checklist)
        .where(Checklist.id == checklist_id)
        .options(selectinload(Checklist.items))
    )

    if for_update:
        statement = statement.with_for_update()

    checklist = db.scalar(statement)

    if checklist is None:
        raise HTTPException(
            status_code=404,
            detail="Шаблон чекліста не знайдено",
        )

    return checklist


def get_checklists(
    db: Session,
    offset: int = 0,
    limit: int = 50,
) -> list[Checklist]:
    statement = (
        select(Checklist)
        .options(selectinload(Checklist.items))
        .order_by(Checklist.id)
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def _ensure_not_used(
    db: Session,
    checklist_id: int,
) -> None:
    execution_id = db.scalar(
        select(ChecklistExecution.id)
        .where(
            ChecklistExecution.checklist_id == checklist_id
        )
        .limit(1)
    )

    if execution_id is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                "Шаблон уже використовується. "
                "Для змін створіть новий шаблон"
            ),
        )


def _commit(db: Session) -> None:
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise


def _build_items(data: ChecklistCreate) -> list[ChecklistItem]:
    return [
        ChecklistItem(**item.model_dump())
        for item in sorted(
            data.items,
            key=lambda item: item.sort_order,
        )
    ]


def create_checklist(
    db: Session,
    data: ChecklistCreate,
) -> Checklist:
    checklist = Checklist(
        name=data.name,
        description=data.description,
        items=_build_items(data),
    )

    db.add(checklist)
    _commit(db)

    return get_checklist(db, checklist.id)


def update_checklist(
    db: Session,
    checklist_id: int,
    data: ChecklistUpdate,
) -> Checklist:
    checklist = get_checklist(
        db, checklist_id, for_update=True
    )

    _ensure_not_used(db, checklist.id)

    checklist.name = data.name
    checklist.description = data.description
    checklist.items = _build_items(data)

    _commit(db)

    return get_checklist(db, checklist.id)


def delete_checklist(
    db: Session,
    checklist_id: int,
) -> None:
    checklist = get_checklist(
        db, checklist_id, for_update=True
    )

    _ensure_not_used(db, checklist.id)

    try:
        db.delete(checklist)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise