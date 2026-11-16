
import datetime
from sqlalchemy import DateTime
from sqlalchemy import Integer


from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey


class Component(Base):
    __tablename__ = "components"

    id: Mapped[int] = mapped_column(primary_key=True)
    drone_id: Mapped[int] = mapped_column(
        ForeignKey("drones.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    serial_number: Mapped[str] = mapped_column(String, nullable=False)
    installed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        nullable=False)
    operating_hours: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    removed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    drone: Mapped["Drone"] = relationship(back_populates="components")
