# users/schemas.py
from pydantic import BaseModel

class UserCreate(BaseModel):
    nom:   str
    email: str
    password: str
    role: str

class UserResponse(BaseModel):
    id: int
    nom:   str
    email: str
    role: str
    is_active: bool

class UserUpdate(BaseModel):
    nom:   str
    email: str | None = None
    role: str | None = None
    is_active: bool | None = None