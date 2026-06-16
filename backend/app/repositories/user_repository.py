from typing import Optional

from sqlalchemy.orm import Session

from ..models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[User]:
        return self.db.query(User).order_by(User.role.asc(), User.username.asc()).all()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def create(self, **kwargs) -> User:
        user = User(**kwargs)
        self.db.add(user)
        self.db.flush()
        return user

    def update(self, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            setattr(user, key, value)
        self.db.add(user)
        self.db.flush()
        return user

    def count_active(self) -> int:
        return self.db.query(User).filter(User.active.is_(True)).count()

    def get_first_analyst(self) -> Optional[User]:
        return self.db.query(User).filter(User.role == "analyst").order_by(User.id.asc()).first()
