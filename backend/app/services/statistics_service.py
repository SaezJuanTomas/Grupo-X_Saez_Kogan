from collections import Counter

from sqlalchemy.orm import Session

from ..repositories.history_repository import HistoryRepository
from ..repositories.user_repository import UserRepository
from ..repositories.vulnerability_repository import VulnerabilityRepository


class StatisticsService:
    def __init__(self, db: Session):
        self.vuln_repo = VulnerabilityRepository(db)
        self.user_repo = UserRepository(db)
        self.history_repo = HistoryRepository(db)

    def get_dashboard_stats(self) -> dict:
        vulnerabilities = self.vuln_repo.get_all()
        users = self.user_repo.list_all()

        severity_counts = Counter(item.severity for item in vulnerabilities)
        status_counts = Counter(item.status for item in vulnerabilities)

        analyst_activity = []
        for user in users:
            if user.role == "analyst":
                analyst_activity.append({
                    "username": user.username,
                    "assigned": self.vuln_repo.count_by_analyst(user.id),
                    "updated": self.history_repo.count_by_actor(user.id),
                })

        return {
            "critical": self.vuln_repo.count_high_irc(8),
            "pending": sum(1 for item in vulnerabilities if item.status == "Pendiente"),
            "resolved": sum(1 for item in vulnerabilities if item.status == "Resuelto"),
            "active_users": self.user_repo.count_active(),
            "severity_counts": dict(severity_counts),
            "status_counts": dict(status_counts),
            "analyst_activity": analyst_activity,
            "irc_distribution": {
                "0-3": self.vuln_repo.count_in_range(0, 3),
                "3-6": self.vuln_repo.count_in_range(3, 6),
                "6-8": self.vuln_repo.count_in_range(6, 8),
                "8-10": self.vuln_repo.count_in_range(8, 100),
            },
        }
