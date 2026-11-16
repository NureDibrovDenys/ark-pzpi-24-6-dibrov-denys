from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

class TelemetrySession(Base):
    __tablename__ = "telemetry_sessions"
    
    __table_args__ = (
        CheckConstraint(
            "ended_at IS NULL OR ended_at >= started_at",
            name="check_telemetry_session_dates"
        ),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    servise_session_id: Mapped[int] = mapped_column(
        ForeignKey("service_session.id"),
        nullable=False,
        index=True
    )
    
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    
    service_session: Mapped["ServiceSession"] = relationship(back_populates="telemetry_sessions")
    
    measurements: Mapped[list["TelemetryMeasurement"]] = relationship(
        back_populates="telemetry_session",
    )