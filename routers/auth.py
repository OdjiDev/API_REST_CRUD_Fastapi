# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlmodel import Session
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

from database.session import get_session
from users import services  # Import de la logique CRUD des utilisateurs
from users.models import User

load_dotenv()

# 1. Initialisation du Routeur pour le Main
router = APIRouter(
    prefix="/auth",
    tags=["Authentification"]
)

# Configuration standard OAuth2 : indique à Swagger où récupérer le Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# 2. Modèles Pydantic pour la validation des données entrantes/sortantes
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str  # "student" ou "teacher"

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool


# 3. Fonctions utilitaires pour la gestion des jetons JWT
def create_access_token(data: dict):
    """Génère un Token JWT signé qui expire après X minutes"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=int(os.getenv("JWT_EXPIRE_MINUTES", 30)))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, os.getenv("JWT_SECRET"), algorithm=os.getenv("JWT_ALGORITHM"))

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)) -> User:
    """
    Le gardien de sécurité de ton API.
    Cette fonction extrait le token, le décode, et vérifie l'identité de l'utilisateur.
    """
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
        
    db_user = services.get_by_email(db, email=email)
    if db_user is None:
        raise credentials_exception
    return db_user


# 4. Les Endpoints (Inscriptions & Connexion)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_session)):
    """Route d'inscription publique"""
    # 1. Validation stricte du rôle
    if user_in.role not in ["student", "teacher"]:
        raise HTTPException(status_code=400, detail="Le rôle doit être 'student' ou 'teacher'.")
        
    # 2. Vérification de l'existence de l'email
    existing_user = services.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Cet email existe déjà.")
        
    # 3. Création et hachage automatiques via le service
    return services.create(db, user_in)


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    """
    Route de connexion.
    OAuth2PasswordRequestForm attend obligatoirement 'username' (l'email) et 'password'.
    """
    # 1. Vérifier l'existence et le mot de passe (via bcrypt)
    db_user = services.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect."
        )
        
    # 2. Construire les données du badge d'accès
    token_data = {"sub": db_user.email, "role": db_user.role, "user_id": db_user.id}
    access_token = create_access_token(data=token_data)
    
    # 3. Retourner le token au format standard attendu par le protocole OAuth2 (et ton futur Front-end)
    return {"access_token": access_token, "token_type": "bearer"}