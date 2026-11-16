
from datetime import datetime, timezone
from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, DateTime, null



class ChecklistExecution(Base):
    __tablename__ = "checklist_execution"

    id: Mapped[int] = mapped_column(primary_key=True)

    checklist_id: Mapped[int] = mapped_column(
        ForeignKey("checklists.id"), nullable=False)
    service_session_id: Mapped[int] = mapped_column(
        ForeignKey("service_session.id"), nullable=False)

    started_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc), nullable=False)

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="in_progress",
        nullable=False
    )

    checklist: Mapped["Checklist"] = relationship()

    service_session: Mapped["ServiceSession"] = relationship()

    answers: Mapped[list["ChecklistAnswer"]] = relationship(
        back_polutes="execution", cascade="all, delete-orphan")

    checklist: Mapped["Checklist"] = relationship(
        back_populates="executions"
    )

    service_session: Mapped["ServiceSession"] = relationship(
        back_populates="checklist_executions"
    )
