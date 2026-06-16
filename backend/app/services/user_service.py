from typing import Optional

from sqlalchemy.orm import Session

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
        results = []
        for user in users:
            assigned_count = self.vuln_repo.count_by_analyst(user.id)
            results.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "active": user.active,
                "latest_activity": user.latest_activity,
                "assigned_vulnerabilities": assigned_count,
            })
        return results

    def create_user(self, username: str, email: str, role: str, password: str) -> User:
        hashed = hash_password(password)
        return self.user_repo.create(
            username=username, email=email, role=role, password=hashed
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
            "role": user.role,
            "active": user.active,
            "latest_activity": user.latest_activity,
            "assigned_vulnerabilities": assigned_count,
        }
