# routers/auth.py
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from sqlmodel import Session
from database.session import get_session
from users import services  # On importe correctement notre module de services

# 1. INITIALISATION DU ROUTEUR (Ce qui causait le NameError)
router = APIRouter(
    prefix="/auth",
    tags=["Authentification"]
)

# 2. MODÈLES PYDANTIC (Les DTO de Validation)
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool


# 3. LES ROUTES DE L'API
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_session)):
    # 1. Validation du rôle
    if user_in.role not in ["student", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Le rôle doit être 'student' ou 'teacher'."
        )
        
    # 2. Appel au service pour vérifier si l'email existe déjà
    existing_user = services.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cet email existe déjà."
        )
        
    # 3. Appel au service pour l'enregistrement (CRUD pur)
    return services.create(db, user_in)