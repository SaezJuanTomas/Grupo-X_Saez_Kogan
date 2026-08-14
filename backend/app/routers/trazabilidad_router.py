from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..core.deps import get_current_user
from ..database import get_db
from ..models import User
from ..repositories.ingestion_repository import IngestionLogRepository
from ..schemas import DetectionSummary, IngestionLogPage, IngestionLogRead

router = APIRouter(prefix="/trazabilidad", tags=["trazabilidad"])


@router.get("/ingestion", response_model=IngestionLogPage)
def list_ingestion_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    repo = IngestionLogRepository(db)
    total = repo.count()
    items = repo.list_all(page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size if total else 0
    return IngestionLogPage(
        items=[IngestionLogRead.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/deteccion", response_model=DetectionSummary)
def detection_summary(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return IngestionLogRepository(db).detection_summary()
