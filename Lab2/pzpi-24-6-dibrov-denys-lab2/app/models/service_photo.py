from datetime import datetime, timezone
from stringprep import map_table_b2

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import service_session
from database import Base

class ServicePhoto(Base):
    __tablename__ = "service_photos"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    service_session_id: Mapped[int] = mapped_column(
        ForeignKey("service_session.id"),
        nullable=False,
        index=True
    )
    
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        unique=True
    )
    
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    
    service_session: Mapped["ServiceSession"] = relationship(back_populates="photos")