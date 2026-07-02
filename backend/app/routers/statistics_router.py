from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..core.deps import get_current_user
from ..database import get_db
from ..models import User, Vulnerability
from ..schemas import DashboardStats, TrendPoint, TrendsResponse
from ..services.statistics_service import StatisticsService

router = APIRouter(tags=["statistics"])


@router.get("/estadisticas", response_model=DashboardStats)
def get_statistics(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return StatisticsService(db).get_dashboard_stats()


@router.get("/estadisticas/tendencias", response_model=TrendsResponse)
def get_trends(
    days: int = Query(default=7, ge=1, le=90),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    cutoff = datetime.utcnow() - timedelta(days=days)

    created_rows = (
        db.query(func.date(Vulnerability.created_at).label("day"), func.count().label("count"))
        .filter(Vulnerability.created_at >= cutoff)
        .group_by(func.date(Vulnerability.created_at))
        .order_by(func.date(Vulnerability.created_at))
        .all()
    )

    from ..models import VulnerabilityStatus
    resolved_rows = (
        db.query(func.date(Vulnerability.updated_at).label("day"), func.count().label("count"))
        .filter(Vulnerability.updated_at >= cutoff, Vulnerability.status == VulnerabilityStatus.RESUELTO)
        .group_by(func.date(Vulnerability.updated_at))
        .order_by(func.date(Vulnerability.updated_at))
        .all()
    )

    created_map = {}
    resolved_map = {}
    for i in range(days):
        day = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        created_map[day] = 0
        resolved_map[day] = 0

    for row in created_rows:
        day = row.day.strftime("%Y-%m-%d") if hasattr(row.day, "strftime") else str(row.day)
        created_map[day] = row.count

    for row in resolved_rows:
        day = row.day.strftime("%Y-%m-%d") if hasattr(row.day, "strftime") else str(row.day)
        resolved_map[day] = row.count

    created = [TrendPoint(date=d, count=created_map[d]) for d in sorted(created_map.keys())]
    resolved = [TrendPoint(date=d, count=resolved_map[d]) for d in sorted(resolved_map.keys())]

    return TrendsResponse(created=created, resolved=resolved)
