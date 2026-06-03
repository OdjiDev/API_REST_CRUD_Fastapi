# routers/auth.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List
from passlib.context import CryptContext

# On crée un Routeur au lieu d'une application complète
router = APIRouter(
    prefix="/auth",        # Toutes les routes de ce fichier commenceront par /auth
    tags=["Authentification"] # Aligné automatiquement dans la doc
)

# Correction du bug passlib/bcrypt pour les versions récentes de Python
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__ident="2b"  # Force l'utilisation de la version stable de l'algorithme
)

# Fausse base de données locale à ce module
fake_users_db = []

# Nos modèles Pydantic
class UserCreate(BaseModel):
    email: str
    password: str
    role: str

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool

# Route d'inscription (Devient automatiquement : /auth/register)
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate):
    if user_in.role not in ["student", "teacher"]:
        raise HTTPException(status_code=400, detail="Le rôle doit être 'student' ou 'teacher'.")
        
    for user in fake_users_db:
        if user["email"] == user_in.email:
            raise HTTPException(status_code=400, detail="Cet email existe déjà.")
            
    hashed_password = pwd_context.hash(user_in.password)
    new_user = {
        "id": len(fake_users_db) + 1,
        "email": user_in.email,
        "hashed_password": hashed_password,
        "role": user_in.role,
        "is_active": True
    }
    fake_users_db.append(new_user)
    return new_user