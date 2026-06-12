from sqlmodel import Session, select
from typing import List, Optional
from .models import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    # ----- Lecture -----
    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        return self.db.exec(stmt).first()

    def get_by_telephone(self, telephone: str) -> Optional[User]:
        stmt = select(User).where(User.telephone == telephone)
        return self.db.exec(stmt).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        stmt = select(User).offset(skip).limit(limit)
        return self.db.exec(stmt).all()

    # ----- Écriture -----
    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()