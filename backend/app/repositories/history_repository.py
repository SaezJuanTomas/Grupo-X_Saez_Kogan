from typing import Optional

from sqlalchemy.orm import Session

from ..models import HistoryLog


class HistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_vulnerability(self, vulnerability_id: Optional[int] = None) -> list[HistoryLog]:
        query = self.db.query(HistoryLog)
        if vulnerability_id:
            query = query.filter(HistoryLog.vulnerability_id == vulnerability_id)
        return query.order_by(HistoryLog.created_at.asc()).all()

    def create(self, **kwargs) -> HistoryLog:
        entry = HistoryLog(**kwargs)
        self.db.add(entry)
        self.db.flush()
        return entry

    def count_by_actor(self, actor_id: int) -> int:
        return self.db.query(HistoryLog).filter(HistoryLog.actor_id == actor_id).count()
