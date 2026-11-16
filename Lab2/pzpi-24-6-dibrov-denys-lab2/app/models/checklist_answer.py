from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ChecklistAnswerStatus
from database import Base


class ChecklistAnswer(Base):
    __tablename__ = "checklist_answers"

    __table_args__ = (
        UniqueConstraint(
            "execution_id",
            "checklist_items_id",
            name="uq_checklist_answer_execution_item",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    execution_id: Mapped[int] = mapped_column(
        ForeignKey("checklist_execution.id"),
        nullable=False,
    )

    checklist_items_id: Mapped[int] = mapped_column(
        ForeignKey("checklist_items.id"),
        nullable=False,
    )

    status: Mapped[ChecklistAnswerStatus] = mapped_column(
        SQLAlchemyEnum(
            ChecklistAnswerStatus,
            name="checklist_answer_status",
        ),
        nullable=False,
    )

    comment: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    execution: Mapped["ChecklistExecution"] = relationship(
        back_populates="answers",
    )

    checklist_item: Mapped["ChecklistItem"] = relationship(
        back_populates="answers",
    )