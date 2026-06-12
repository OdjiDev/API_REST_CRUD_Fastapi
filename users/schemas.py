from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional
from .models import UserRole, UserStatus

# ---------- Création (inscription) ----------
class UserCreate(BaseModel):
    nom: str = Field(..., min_length=2, max_length=100)
    prenom: str = Field(..., min_length=2, max_length=100)
    telephone: str = Field(..., pattern=r'^\+?[0-9]{8,20}$')
    email: EmailStr
    password: str = Field(..., min_length=6)  # sera hashé
    role: UserRole = UserRole.STUDENT
    photo_profil: Optional[str] = None
    ville_id: Optional[int] = None
    adresse: Optional[str] = None
    # statut: on ne le donne pas à la création, valeur par défaut PENDING

    @validator('email')
    def normalize_email(cls, v):
        return v.lower().strip()

# ---------- Réponse (ce que l’API renvoie) ----------
class UserResponse(BaseModel):
    id: int
    nom: str
    prenom: str
    telephone: str
    email: str
    role: UserRole
    photo_profil: Optional[str]
    ville_id: Optional[int]
    adresse: Optional[str]
    statut: UserStatus
    is_active: bool   # pour compatibilité frontend
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @validator('is_active', pre=True, always=True)
    def compute_is_active(cls, v, values):
        # Si le modèle a un attribut statut, on le convertit
        if 'statut' in values:
            return values['statut'] == UserStatus.ACTIVE
        return v

# ---------- Mise à jour (modification partielle) ----------
class UserUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    photo_profil: Optional[str] = None
    ville_id: Optional[int] = None
    adresse: Optional[str] = None
    statut: Optional[UserStatus] = None
    is_active: Optional[bool] = None   # si on utilise is_active à la place de statut

    @validator('email')
    def normalize_email(cls, v):
        if v:
            return v.lower().strip()
        return v

# ---------- Changement de mot de passe ----------
class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)

# ---------- Login (pour compatibilité avec l’existant) ----------
class UserLoginJSON(BaseModel):
    email: str
    password: str