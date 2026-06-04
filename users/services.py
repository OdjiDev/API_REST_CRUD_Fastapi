# users/services.py
from sqlmodel import Session, select
import bcrypt
from users.models import User
from users.schemas import UserCreate, UserUpdate

def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)

def get_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return db.exec(statement).first()

def get_all(db: Session, skip: int = 0, limit: int = 100):
    statement = select(User).offset(skip).limit(limit)
    return db.exec(statement).all()

def create(db: Session, user_in: UserCreate) -> User:
    # Sécurité de base : on ne stocke jamais un mot de passe en clair
    password_bytes = user_in.password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        role=user_in.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update(db: Session, db_user: User, user_update: UserUpdate) -> User:
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete(db: Session, db_user: User) -> None:
    db.delete(db_user)
    db.commit()