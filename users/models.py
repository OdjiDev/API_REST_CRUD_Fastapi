from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"

class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(max_length=100)
    prenom: str = Field(max_length=100)
    telephone: str = Field(max_length=20, unique=True)
    email: str = Field(max_length=255, unique=True, index=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.STUDENT)
    photo_profil: Optional[str] = Field(default=None, max_length=500)
    ville_id: Optional[int] = Field(default=None)  # clé étrangère vers table villes
    adresse: Optional[str] = Field(default=None, max_length=255)
    statut: UserStatus = Field(default=UserStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Pour compatibilité avec l'existant : is_active dérivé
    @property
    def is_active(self) -> bool:
        return self.statut == UserStatus.ACTIVE