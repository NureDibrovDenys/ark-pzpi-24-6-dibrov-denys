



from operator import sub

from fastapi import HTTPException, status
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jwt import InvalidTokenError

from app.core.security import decode_access_token
from app.models.user import User
from app.core.enums import UserRole
from database import get_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
)-> User:
    credetnials_error = HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail = "Недійсний або прострочений токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_access_token(token)
        subject = payload.get("sub")
        
        if not isinstance(subject, str): 
            raise credetnials_error
        user_id = int(subject)
        
        if user_id <= 0:
            raise credetnials_error
        
        
    except(InvalidTokenError, ValueError, TypeError):
        raise credetnials_error from None
    
    user = db.get(User, user_id)
    
    if user is None:
        raise credetnials_error
    
    return user 

def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Доступ дозволений лише адміністратору",
        )

    return current_user