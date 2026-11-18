from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.security import DUMMY_PASSWORD_HASH, create_access_token, verify_password
from app.crud.user import (
    EmailAlreadyRegisteredError,
    create_user,
)
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.crud.user import get_user_by_email
from database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    data: UserCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_user(db, data)
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким email вже зареєстрований.",
        )from None

@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неправильний email або пароль",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        email = str(
            TypeAdapter(EmailStr).validate_python(form_data.username)
        )
    except ValidationError:
        raise credentials_error from None
    
    user = get_user_by_email(db, email)
    
    stored_hash = (
        user.password_hash
        if user is not None
        else DUMMY_PASSWORD_HASH
    )
    
    password_is_valid = verify_password(
        form_data.password,
        stored_hash,
    )

    if user is None or not password_is_valid:
        raise credentials_error
    
    return TokenResponse(
        access_token=create_access_token(user.id),
    )
    
@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user