
from app.core.enums import UserRole
from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from sqlalchemy.types import Enum as SQLAlchemyEnum

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    role: Mapped[UserRole] = mapped_column(
        SQLAlchemyEnum(UserRole, name = "user_role"),
        
        default = UserRole.USER,
        server_default = "USER",
        nullable = False
    )
    
    drones: Mapped[list["Drone"]] = relationship(back_populates="owner")


    