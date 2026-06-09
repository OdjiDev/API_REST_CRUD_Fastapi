# users/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from routers.auth import get_current_user  #CTTE LIGNE
from users.models import User
from typing import List
from database.session import get_session
from users.models import User
from users.schemas import UserCreate, UserResponse, UserUpdate
from users import services

from users.schemas import UserResponse  #  schéma de sortie propre
from routers.auth import get_current_user  #  ON IMPORTE LE GARDIEN ICI

router = APIRouter(
    prefix="/users",
    tags=["Utilisateurs"]
)

# ==========================================
#  ROUTE PROFIL : L'UTILISATEUR CONNECTÉ
# ==========================================
@router.get("/me", response_model=UserResponse)
def read_user_me(current_user: User = Depends(get_current_user)):
    """
    Récupère le profil de l'utilisateur actuellement connecté via son token JWT.
    """
    return current_user
# 1. CRÉER
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_session)):
    db_user = services.get_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé.")
    return services.create(db, user_in)
#  ROUTE PROTÉGÉE : Seuls les utilisateurs connectés avec un JWT valide peuvent y accéder
@router.get("/", response_model=List[UserResponse])
def read_users(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)  #  LA PROTECTION EST ICI !
):
    """
    Récupère la liste de tous les utilisateurs.
    FastAPI va automatiquement intercepter la requête, valider le Token JWT, 
    et injecter l'utilisateur connecté dans la variable 'current_user'.
    """
    return services.get_all(db)
# 2. LIRE TOUS
# @router.get("/", response_model=List[UserResponse])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
#     return services.get_all(db, skip=skip, limit=limit)

# 3. LIRE UN SEUL
@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_session)):
    db_user = services.get_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    return db_user

# 4. MODIFIER
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_session)):
    db_user = services.get_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    return services.update(db, db_user, user_update)

# 5. SUPPRIMER
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_session)):
    db_user = services.get_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    services.delete(db, db_user)
    return None