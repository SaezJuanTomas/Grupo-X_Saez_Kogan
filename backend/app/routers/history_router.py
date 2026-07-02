from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.deps import get_current_user
from ..database import get_db
from ..models import User
from ..repositories.history_repository import HistoryRepository
from ..schemas import HistoryLogRead

router = APIRouter(tags=["history"])


@router.get("/historial", response_model=list[HistoryLogRead])
def list_history(
    vulnerability_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return HistoryRepository(db).list_by_vulnerability(vulnerability_id)
