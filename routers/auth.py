# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlmodel import Session
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Optional

from database.session import get_session
from users import services  
from users.models import User
from users.schemas import UserLoginJSON, UserResponse, UserCreate # Import depuis les schémas centralisés

load_dotenv()

router = APIRouter(
    prefix="/auth",
    tags=["Authentification"]
)

# Indique à Swagger où récupérer le Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_access_token(data: dict):
    """Génère un Token JWT signé qui expire après X minutes"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=int(os.getenv("JWT_EXPIRE_MINUTES", 30)))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, os.getenv("JWT_SECRET"), algorithm=os.getenv("JWT_ALGORITHM"))

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)) -> User:
    """Le gardien de sécurité de l'API (validation du JWT)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token d'authentification invalide ou expiré.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM")])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    db_user = services.get_user_by_email(db, email=email)
    if db_user is None:
        raise credentials_exception
    return db_user


# ==========================================
#  ENDPOINTS (Inscription & Connexion)
# ==========================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_session)):
    """Route d'inscription publique"""
    if user_in.role not in ["student", "admin", "teacher"]:
        raise HTTPException(status_code=400, detail="Le rôle doit être 'student', 'teacher' ou 'admin'.")
    
    # Normalisation de la casse (minuscules)
    user_in.email = user_in.email.lower().strip()
        
    existing_user = services.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Cet email existe déjà.")
        
    return services.create(db, user_in)


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), # 💡 On revient à la syntaxe standard et propre de FastAPI
    db: Session = Depends(get_session)
):
    """
    Route de connexion standardisée pour recevoir le Form-Data d'Angular.
    """
    # Pas besoin de json_data ici puisque Angular utilise HttpParams !
    email_clean = form_data.username.lower().strip()

    # Vérification des identifiants (Bcrypt)
    db_user = services.authenticate_user(db, email=email_clean, password=form_data.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect."
        )
        
    # Génération du Token JWT
    token_data = {"sub": db_user.email, "role": db_user.role, "user_id": db_user.id}
    access_token = create_access_token(data=token_data)
    
    return {"access_token": access_token, "token_type": "bearer"}