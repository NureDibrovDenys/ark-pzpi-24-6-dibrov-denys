
import datetime


from sqlalchemy import DateTime

from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String


class ServiceSession(Base):
    __tablename__ = "service_session"

    id: Mapped[int] = mapped_column(primary_key=True)
    drone_id: Mapped[int] = mapped_column(
        ForeignKey("drones.id"), nullable=False)
    started_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)
    ended_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    drone: Mapped["Drone"] = relationship(back_populates="service_sessions")

    checklist_executions: Mapped[list["ChecklistExecution"]] = relationship(
        back_populates="service_session"
    )
