from sqlalchemy.orm import Session

from ..auth import hash_password, verify_password
from ..models import User, UserRole
from ..repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def login(self, username: str, password: str) -> User | None:
        user = self.user_repo.get_by_username(username)
        if not user or not verify_password(password, user.password):
            return None
        if not user.active:
            return None
        return user

    def create_user(self, username: str, email: str, role: str, password: str, active: bool = True) -> User:
        hashed = hash_password(password)
        return self.user_repo.create(
            username=username,
            email=email,
            role=role if isinstance(role, UserRole) else UserRole(role),
            password=hashed,
            active=active,
        )
