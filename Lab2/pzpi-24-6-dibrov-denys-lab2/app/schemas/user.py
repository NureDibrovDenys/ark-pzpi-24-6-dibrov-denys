

from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints

from app.core.enums import UserRole


UserName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=100,
    ),
]

class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    name: UserName
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=8, max_length=128)
    
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    email: EmailStr
    role: UserRole