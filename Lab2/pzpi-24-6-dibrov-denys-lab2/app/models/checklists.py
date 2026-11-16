from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

class Checklist(Base):
    __tablename__ = "checklists"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    items: Mapped[list["ChecklistItem"]] = relationship(
        back_populates="checklist",
        cascade="all, delete-orphan",
        order_by="ChecklistItem.sort_order",
    )
    
    executions: Mapped[list["ChecklistExecution"]] = relationship(
        back_populates="checklist",
    )