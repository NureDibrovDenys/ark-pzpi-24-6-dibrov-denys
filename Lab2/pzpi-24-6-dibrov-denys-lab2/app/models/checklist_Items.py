

from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey


class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    checklist_id: Mapped[int] = mapped_column(
        ForeignKey("checklists.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(150), nullable=False)

    sort_order: Mapped[int] = mapped_column(default=1, nullable=False)
    is_required: Mapped[bool] = mapped_column(default=True, nullable=False)

    checklist: Mapped["Checklist"] = relationship(back_polutes="items")

    answers: Mapped[list["ChecklistAnswer"]] = relationship(
        back_populates="checklist_item"
    )
