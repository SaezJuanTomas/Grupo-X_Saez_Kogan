from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import get_current_user, require_admin
from ..database import get_db
from ..models import User
from ..repositories.history_repository import HistoryRepository
from ..schemas import HistoryLogCreate, HistoryLogRead

router = APIRouter(tags=["history"])


@router.get("/historial", response_model=list[HistoryLogRead])
def list_history(
    vulnerability_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return HistoryRepository(db).list_by_vulnerability(vulnerability_id)


@router.post("/historial", response_model=HistoryLogRead)
def create_history(
    payload: HistoryLogCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_admin),
):
    return HistoryRepository(db).create(**payload.model_dump())
