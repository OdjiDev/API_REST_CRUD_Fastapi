from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from database.session import get_session
from users.models import User
from users.schemas import UserCreate, UserResponse, UserUpdate
from users import services
from routers.auth import get_current_user  # Import unique du gardien JWT

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

# ==========================================
#  1. CRÉER (Normalisation de l'email incluse)
# ==========================================
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_session)):
    # Normalisation préventive pour éviter les soucis de casse (Majuscules/Minuscules)
    email_clean = user_in.email.lower().strip()
    
    db_user = services.get_by_email(db, email=email_clean)
    if db_user:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé.")
        
    # On passe l'objet mis à jour au service
    user_in.email = email_clean
    return services.create(db, user_in)

# ==========================================
#  2. LIRE TOUS (Route Protégée)
# ==========================================
@router.get("/", response_model=List[UserResponse])
def read_users(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère la liste de tous les utilisateurs (Réservé aux membres connectés).
    """
    return services.get_all(db)

# ==========================================
#  3. LIRE UN SEUL (Sécurisé par le Gardien)
# ==========================================
@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int, 
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)  # 🔒 Ajout de la protection
):
    db_user = services.get_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    return db_user

# ==========================================
#  4. MODIFIER (Sécurisé par le Gardien)
# ==========================================
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, 
    user_update: UserUpdate, 
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)  # 🔒 Ajout de la protection
):
    db_user = services.get_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    return services.update(db, db_user, user_update)

# ==========================================
#  5. SUPPRIMER (Sécurisé par le Gardien)
# ==========================================
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int, 
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)  # 🔒 Ajout de la protection
):
    db_user = services.get_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    services.delete(db, db_user)
    return None