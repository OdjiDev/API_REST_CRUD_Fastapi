import bcrypt
from typing import Optional, List
from sqlmodel import Session
from .models import User, UserStatus
from .schemas import UserCreate, UserUpdate
from .user_repo import UserRepository

# ----- Helpers -----
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

# ----- Fonctions exposées (utilisées par les routes) -----
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return UserRepository(db).get_by_id(user_id)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return UserRepository(db).get_by_email(email)

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return UserRepository(db).get_all(skip, limit)

def create_user(db: Session, user_in: UserCreate) -> User:
    repo = UserRepository(db)
    # Vérifications d'unicité (logique métier)
    if repo.get_by_email(user_in.email):
        raise ValueError("Email déjà utilisé")
    if repo.get_by_telephone(user_in.telephone):
        raise ValueError("Téléphone déjà utilisé")

    # Hash du mot de passe
    hashed = hash_password(user_in.password)

    new_user = User(
        nom=user_in.nom,
        prenom=user_in.prenom,
        telephone=user_in.telephone,
        email=user_in.email,
        hashed_password=hashed,
        role=user_in.role,
        photo_profil=user_in.photo_profil,
        ville_id=user_in.ville_id,
        adresse=user_in.adresse,
        statut=UserStatus.PENDING  # ou ACTIVE selon ton besoin
    )
    return repo.create(new_user)

def update_user(db: Session, user: User, user_update: UserUpdate) -> User:
    repo = UserRepository(db)
    update_data = user_update.dict(exclude_unset=True)
    # Conversion de is_active (si présent) vers statut
    if 'is_active' in update_data:
        update_data['statut'] = UserStatus.ACTIVE if update_data.pop('is_active') else UserStatus.SUSPENDED
    for key, value in update_data.items():
        if value is not None:
            setattr(user, key, value)
    return repo.update(user)

def delete_user(db: Session, user: User) -> None:
    UserRepository(db).delete(user)

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    repo = UserRepository(db)
    user = repo.get_by_email(email.lower().strip())
    if not user:
        return None
    if user.statut != UserStatus.ACTIVE:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def change_password(db: Session, user_id: int, old_password: str, new_password: str) -> User:
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise ValueError("Utilisateur non trouvé")
    if not verify_password(old_password, user.hashed_password):
        raise ValueError("Ancien mot de passe incorrect")
    user.hashed_password = hash_password(new_password)
    return repo.update(user)