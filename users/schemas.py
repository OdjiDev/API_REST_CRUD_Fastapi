# users/schemas.py
from pydantic import BaseModel

class UserCreate(BaseModel):
   
    email: str
    password: str
    role: str
    phone: str | None = None

class UserResponse(BaseModel):
    id: int
    
    email: str
    role: str
    phone: str | None = None
    is_active: bool
# Tout au bout de users/schemas.py
class UserLoginJSON(BaseModel):  #  Ajoute bien "JSON" ici
    email: str
    password: str

class UserUpdate(BaseModel):
    
    email: str | None = None
    role: str | None = None
    phone: str | None = None
    is_active: bool | None = None