from app.core.security import hash_password
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.user import UserCreate
from app.core.enums import UserRole

class EmailAlreadyRegisteredError(Exception):
    """Exception raised when trying to register a user with an email that is already in use."""
    pass

def get_user_by_email(db: Session, email:str) -> User | None:
    statement = select(User).where(User.email == email)
    return db.scalar(statement)

def create_user(db: Session, data: UserCreate) -> User:
    email = str(data.email)
    
    if get_user_by_email(db, email) is not None:
        raise EmailAlreadyRegisteredError()
    
    user = User(
        name=data.name,
        email=email,
        password_hash=hash_password(data.password),
        role = UserRole.USER
    )
    
    db.add(user)
    
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        
        if get_user_by_email(db, email) is not None:
            raise EmailAlreadyRegisteredError()
        
        
        raise 
    
    db.refresh(user)
    
    return user
        
        