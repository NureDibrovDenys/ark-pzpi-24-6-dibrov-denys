from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, String, ForeignKey

class ChecklistAnswer(Base):
    __tablename__ = "checklist_answers"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    execution_id: Mapped[int] = mapped_column(ForeignKey("checklist_execution.id"), nullable=False)
    
    checklist_items_id: Mapped[int] = mapped_column(ForeignKey("checklist_items.id"), nullable=False)
    
    is_completed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    
    comment: Mapped[str] = mapped_column(String, nullable=True)
    
    execution: Mapped["ChecklistExecution"] = relationship(
        back_populates="answers"
    )

    checklist_item: Mapped["ChecklistItem"] = relationship()
    
    