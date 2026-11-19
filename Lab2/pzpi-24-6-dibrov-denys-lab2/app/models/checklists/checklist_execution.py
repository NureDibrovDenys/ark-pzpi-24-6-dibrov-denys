from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import CheckListExecutionStatus
from database import Base


class ChecklistExecution(Base):
    __tablename__ = "checklist_execution"

    id: Mapped[int] = mapped_column(primary_key=True)

    checklist_id: Mapped[int] = mapped_column(
        ForeignKey("checklists.id"),
        nullable=False,
    )

    service_session_id: Mapped[int] = mapped_column(
        ForeignKey("service_session.id"),
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    status: Mapped[CheckListExecutionStatus] = mapped_column(
        SQLAlchemyEnum(
            CheckListExecutionStatus,
            name="checklist_execution_status",
        ),
        default=CheckListExecutionStatus.IN_PROGRESS,
        nullable=False,
    )

    checklist: Mapped["Checklist"] = relationship(
        back_populates="executions",
    )

    service_session: Mapped["ServiceSession"] = relationship(
        back_populates="checklist_executions",
    )

    answers: Mapped[list["ChecklistAnswer"]] = relationship(
        back_populates="execution",
        cascade="all, delete-orphan",
    )