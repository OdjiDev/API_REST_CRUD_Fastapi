# routers/auth.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List
import bcrypt  # Importation directe pour un hachage robuste
import jwt     # Importation pour générer les tokens de connexion
from datetime import datetime, timedelta

# On crée le Routeur
router = APIRouter(
    prefix="/auth",        # Toutes les routes commenceront par /auth
    tags=["Authentification"]
)

# CONFIGURATION JWT (Clés de chiffrement des tokens)
SECRET_KEY = "SUPER_SECRET_MALI_TECH_KEY_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Base de données temporaire en mémoire
fake_users_db = []


# --- 1. MODÈLES PYDANTIC (Validation des données) ---

class UserCreate(BaseModel):
    email: str
    password: str
    role: str

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool

# Modèle pour ce que l'utilisateur envoie au login
class UserLogin(BaseModel):
    email: str
    password: str

# Modèle pour la réponse contenant le Token
class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# --- 2. FONCTION UTILITAIRE JWT ---

def create_access_token(data: dict):
    """Génère un jeton JWT sécurisé et signé avec une date d'expiration"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- 3. ENDPOINTS (ROUTES API) ---

# A. Route d'Inscription (/auth/register)
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate):
    # Validation du rôle
    if user_in.role not in ["student", "teacher"]:
        raise HTTPException(status_code=400, detail="Le rôle doit être 'student' ou 'teacher'.")
        
    # Vérification des doublons d'email
    for user in fake_users_db:
        if user["email"] == user_in.email:
            raise HTTPException(status_code=400, detail="Cet email existe déjà.")
            
    # Hachage sécurisé du mot de passe avec bcrypt natif
    password_bytes = user_in.password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

    # Enregistrement du nouvel utilisateur
    new_user = {
        "id": len(fake_users_db) + 1,
        "email": user_in.email,
        "hashed_password": hashed_password,
        "role": user_in.role,
        "is_active": True
    }
    fake_users_db.append(new_user)
    return new_user


# B. Route de Connexion (/auth/login)
@router.post("/login", response_model=TokenResponse)
def login(user_credentials: UserLogin):
    # 1. Recherche de l'utilisateur par son email
    user_found = None
    for user in fake_users_db:
        if user["email"] == user_credentials.email:
            user_found = user
            break
            
    if not user_found:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Identifiants incorrects (Email)."
        )
        
    # 2. Vérification du mot de passe avec bcrypt.checkpw
    password_bytes = user_credentials.password.encode('utf-8')
    hashed_db_bytes = user_found["hashed_password"].encode('utf-8')
    
    if not bcrypt.checkpw(password_bytes, hashed_db_bytes):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Identifiants incorrects (Mot de passe)."
        )
        
    # 3. Génération et signature du Token JWT si tout est correct
    token_data = {"sub": user_found["email"], "role": user_found["role"]}
    token = create_access_token(data=token_data)
    
    return {"access_token": token, "token_type": "bearer"}