from datetime import datetime

from fastapi import telemetry
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Double,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

class TelemetryMeasurement(Base):
    __tablename__ = "telemetry_measurements"
    
    __table_args__ = (
        CheckConstraint(
            "voltage_v >= 0",
            name="check_telemetry_measurement_voltage",
        ),
        Index(
            "index_telemetry_measurements_session_time",
            "telemetry_session_id",
            "measured_at",
        )
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    telemetry_session_id: Mapped[int] = mapped_column(
        ForeignKey("telemetry_sessions.id"),
        nullable=False,
      
    )
#час отримання показників
    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    
    acceleration_x: Mapped[float] = mapped_column(
        Double,
        nullable=False,
    )
    
    acceleration_y: Mapped[float] = mapped_column(
        Double,
        nullable=False,
    )
    
    acceleration_z: Mapped[float] = mapped_column(
        Double,
        nullable=False,
    )
    
    temperature_c: Mapped[float] = mapped_column(
        Double,
        nullable=False,
    )
    
    voltage_v: Mapped[float] = mapped_column(
        Double,
        nullable=False,
    )
    
    telemetry_session: Mapped["TelemetrySession"] = relationship(
        back_populates="measurements",
    )