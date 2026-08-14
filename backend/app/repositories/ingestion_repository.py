from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import VulnerabilityIngestionLog


class IngestionLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> VulnerabilityIngestionLog:
        entry = VulnerabilityIngestionLog(**kwargs)
        self.db.add(entry)
        self.db.flush()
        return entry

    def list_all(self, page: int = 1, page_size: int = 50) -> list[VulnerabilityIngestionLog]:
        offset = (page - 1) * page_size
        return (
            self.db.query(VulnerabilityIngestionLog)
            .order_by(VulnerabilityIngestionLog.inserted_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

    def count(self) -> int:
        return self.db.query(VulnerabilityIngestionLog).count()

    def detection_summary(self) -> dict:
        rows = (
            self.db.query(
                func.count(VulnerabilityIngestionLog.id).label("total"),
                func.avg(VulnerabilityIngestionLog.detection_delta_seconds).label("avg_seconds"),
                func.min(VulnerabilityIngestionLog.detection_delta_seconds).label("min_seconds"),
                func.max(VulnerabilityIngestionLog.detection_delta_seconds).label("max_seconds"),
                func.count(VulnerabilityIngestionLog.detection_delta_seconds).label("with_delta"),
            )
            .one()
        )
        total = rows.total or 0
        with_delta = rows.with_delta or 0
        return {
            "total_registros": total,
            "con_delta_medible": with_delta,
            "sin_nvd_published": total - with_delta,
            "avg_seconds": int(rows.avg_seconds) if rows.avg_seconds is not None else None,
            "min_seconds": int(rows.min_seconds) if rows.min_seconds is not None else None,
            "max_seconds": int(rows.max_seconds) if rows.max_seconds is not None else None,
        }
