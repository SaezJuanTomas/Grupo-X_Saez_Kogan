from typing import Optional, Tuple

from sqlalchemy.orm import Session

from ..auth import create_access_token, hash_password, verify_password
from ..models import User
from ..repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def login(self, username: str, password: str) -> Optional[Tuple[str, User]]:
        user = self.user_repo.get_by_username(username)
        if not user or not verify_password(password, user.password):
            return None
        token = create_access_token({"sub": user.id, "role": user.role})
        return token, user

    def create_user(self, username: str, email: str, role: str, password: str, active: bool = True) -> User:
        hashed = hash_password(password)
        return self.user_repo.create(
            username=username, email=email, role=role, password=hashed, active=active
        )
