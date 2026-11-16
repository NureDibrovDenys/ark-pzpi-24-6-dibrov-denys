
from sqlalchemy import Integer


from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from app.core.enums import DroneStatus
from sqlalchemy import Enum as SQLAlchemyEnum


class Drone(Base):
    __tablename__ = "drones"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    manufacturer: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    max_flight_time: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[DroneStatus] = mapped_column(SQLAlchemyEnum(DroneStatus), default=DroneStatus.WORKING, nullable=False)
    service_sessions: Mapped[list["ServiceSession"]] = relationship(back_populates= "drone")
    components: Mapped[list["Component"]] = relationship(back_populates= "drone")
    

