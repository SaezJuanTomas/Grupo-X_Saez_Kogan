from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..auth import get_current_user
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
    vulnerabilities = db.query(Vulnerability).filter(Vulnerability.created_at >= cutoff).all()

    created_map: dict[str, int] = {}
    resolved_map: dict[str, int] = {}
    for i in range(days):
        day = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        created_map[day] = 0
        resolved_map[day] = 0

    for v in vulnerabilities:
        day = v.created_at.strftime("%Y-%m-%d")
        created_map[day] = created_map.get(day, 0) + 1
        if v.status == "Resuelto":
            day_r = v.updated_at.strftime("%Y-%m-%d")
            resolved_map[day_r] = resolved_map.get(day_r, 0) + 1

    created = [TrendPoint(date=d, count=created_map[d]) for d in sorted(created_map.keys())]
    resolved = [TrendPoint(date=d, count=resolved_map[d]) for d in sorted(resolved_map.keys())]

    return TrendsResponse(created=created, resolved=resolved)
