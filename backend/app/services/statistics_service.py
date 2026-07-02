from collections import Counter

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import Severity, User, UserRole, Vulnerability, VulnerabilityStatus
from ..repositories.history_repository import HistoryRepository
from ..repositories.user_repository import UserRepository
from ..repositories.vulnerability_repository import VulnerabilityRepository


class StatisticsService:
    def __init__(self, db: Session):
        self.db = db
        self.vuln_repo = VulnerabilityRepository(db)
        self.user_repo = UserRepository(db)
        self.history_repo = HistoryRepository(db)

    def get_dashboard_stats(self) -> dict:
        severity_counts_raw = dict(
            self.db.query(Vulnerability.severity, func.count())
            .group_by(Vulnerability.severity)
            .all()
        )
        severity_counts = {}
        for k, v in severity_counts_raw.items():
            key = k.value if hasattr(k, "value") else str(k)
            severity_counts[key] = v

        status_counts_raw = dict(
            self.db.query(Vulnerability.status, func.count())
            .group_by(Vulnerability.status)
            .all()
        )
        status_counts = {}
        for k, v in status_counts_raw.items():
            key = k.value if hasattr(k, "value") else str(k)
            status_counts[key] = v

        analysts = (
            self.db.query(User)
            .filter(User.role == UserRole.ANALYST, User.active == True)
            .all()
        )
        analyst_ids = [a.id for a in analysts]
        assignments = dict(
            self.db.query(Vulnerability.assigned_analyst_id, func.count())
            .filter(Vulnerability.assigned_analyst_id.in_(analyst_ids))
            .group_by(Vulnerability.assigned_analyst_id)
            .all()
        ) if analyst_ids else {}

        analyst_activity = []
        for analyst in analysts:
            analyst_activity.append({
                "username": analyst.username,
                "assigned": assignments.get(analyst.id, 0),
                "updated": self.history_repo.count_by_actor(analyst.id),
            })

        irc_counts = {
            "0-3": self.vuln_repo.count_in_range(0, 3),
            "3-6": self.vuln_repo.count_in_range(3, 6),
            "6-8": self.vuln_repo.count_in_range(6, 8),
            "8-10": self.vuln_repo.count_in_range(8, 100),
        }

        return {
            "critical": severity_counts.get("Crítica", 0),
            "pending": status_counts.get("Pendiente", 0),
            "resolved": status_counts.get("Resuelto", 0),
            "active_users": self.user_repo.count_active(),
            "severity_counts": severity_counts,
            "status_counts": status_counts,
            "analyst_activity": analyst_activity,
            "irc_distribution": irc_counts,
        }
