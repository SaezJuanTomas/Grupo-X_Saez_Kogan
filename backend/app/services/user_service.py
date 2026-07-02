from typing import Optional

from sqlalchemy.orm import Session, joinedload

from ..auth import hash_password
from ..models import User
from ..repositories.user_repository import UserRepository
from ..repositories.vulnerability_repository import VulnerabilityRepository


class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.vuln_repo = VulnerabilityRepository(db)

    def list_users(self) -> list[dict]:
        users = self.user_repo.list_all()
        user_ids = [u.id for u in users]
        counts = self.vuln_repo.count_by_analysts(user_ids) if user_ids else {}

        results = []
        for user in users:
            results.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value if hasattr(user.role, "value") else user.role,
                "active": user.active,
                "latest_activity": user.latest_activity,
                "assigned_vulnerabilities": counts.get(user.id, 0),
            })
        return results

    def create_user(self, username: str, email: str, role: str, password: str) -> User:
        existing = self.user_repo.get_by_username(username)
        if existing:
            from ..core.exceptions import DuplicateResourceError
            raise DuplicateResourceError(f"El usuario '{username}' ya existe")
        hashed = hash_password(password)
        return self.user_repo.create(
            username=username,
            email=email,
            role=role,
            password=hashed,
        )

    def update_user(self, user_id: int, changes: dict) -> Optional[dict]:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None

        if "password" in changes:
            changes["password"] = hash_password(changes["password"])

        self.user_repo.update(user, **changes)

        assigned_count = self.vuln_repo.count_by_analyst(user.id)
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value if hasattr(user.role, "value") else user.role,
            "active": user.active,
            "latest_activity": user.latest_activity,
            "assigned_vulnerabilities": assigned_count,
        }
