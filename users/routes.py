# users/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from database.session import get_session
from users.models import User, UserRole, UserStatus
from users.schemas import (
    UserCreate, UserResponse, UserUpdate, PasswordChange
)
from users import services  # tes fonctions service (qui utilisent le repository)
from routers.auth import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Utilisateurs"]
)


# ==========================================
#  PROFIL CONNECTÉ
# ==========================================
@router.get("/me", response_model=UserResponse)
def read_user_me(current_user: User = Depends(get_current_user)):
    """
    Récupère le profil de l'utilisateur actuellement connecté.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_my_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Modifier son propre profil (sauf le rôle, le statut).
    """
    # On interdit la modification du rôle et du statut via cette route
    if user_update.role is not None or user_update.statut is not None:
        raise HTTPException(status_code=403, detail="Vous ne pouvez pas modifier votre rôle ou statut")
    updated = services.update_user(db, current_user, user_update)
    return updated


# ==========================================
#  CHANGEMENT DE MOT DE PASSE (connecté)
# ==========================================
@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_my_password(
    passwords: PasswordChange,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Change le mot de passe de l'utilisateur connecté.
    """
    try:
        services.change_password(db, current_user.id, passwords.old_password, passwords.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return


# ==========================================
#  CRÉATION D'UN UTILISATEUR (inscription)
# ==========================================
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_session)):
    """
    Inscription d'un nouvel utilisateur.
    """
    # La normalisation email est déjà faite dans le schéma UserCreate
    try:
        user = services.create_user(db, user_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return user


# ==========================================
#  LISTE DE TOUS LES UTILISATEURS (protégé)
# ==========================================
@router.get("/", response_model=List[UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère la liste paginée des utilisateurs.
    (Réservé aux utilisateurs authentifiés)
    """
    # Optionnel : restreindre l'accès aux admins/teachers
    # if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
    #     raise HTTPException(403, "Accès non autorisé")
    return services.get_all_users(db, skip=skip, limit=limit)


# ==========================================
#  LECTURE D'UN SEUL UTILISATEUR
# ==========================================
@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Détail d'un utilisateur par son ID.
    """
    user = services.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    return user


# ==========================================
#  MODIFICATION D'UN UTILISATEUR (par admin ou propriétaire)
# ==========================================
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Modifie un utilisateur.
    Seul l'admin ou l'utilisateur lui-même peut modifier.
    """
    user = services.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    # Vérification des droits
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Action non autorisée")
    # Un utilisateur non-admin ne peut pas changer son rôle ni son statut
    if current_user.id == user_id and current_user.role != UserRole.ADMIN:
        if user_update.role is not None or user_update.statut is not None:
            raise HTTPException(status_code=403, detail="Vous ne pouvez pas modifier votre rôle ou statut")
    updated = services.update_user(db, user, user_update)
    return updated


# ==========================================
#  SUPPRESSION D'UN UTILISATEUR
# ==========================================
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Supprime un utilisateur.
    Seul l'admin ou l'utilisateur lui-même peut supprimer.
    """
    user = services.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Action non autorisée")
    services.delete_user(db, user)
    return


# ==========================================
#  ADMIN : SUSPENDRE UN UTILISATEUR
# ==========================================
@router.patch("/{user_id}/suspend", response_model=UserResponse)
def suspend_user(
    user_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Suspendre un utilisateur (admin seulement).
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin requis")
    user = services.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    if user.role == UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Impossible de suspendre un administrateur")
    user.statut = UserStatus.SUSPENDED
    updated = services.update_user(db, user, UserUpdate(statut=UserStatus.SUSPENDED))
    return updated


# ==========================================
#  ADMIN : ACTIVER UN UTILISATEUR
# ==========================================
@router.patch("/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Activer un utilisateur (admin seulement).
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin requis")
    user = services.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    user.statut = UserStatus.ACTIVE
    updated = services.update_user(db, user, UserUpdate(statut=UserStatus.ACTIVE))
    return updated