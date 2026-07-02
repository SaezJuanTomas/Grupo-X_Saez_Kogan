from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.deps import get_current_user
from ..database import get_db
from ..models import User
from ..schemas import CommentCreate, CommentRead
from ..services.vulnerability_service import VulnerabilityService

router = APIRouter(tags=["comments"])


@router.get("/comentarios", response_model=list[CommentRead])
def list_comments(
    vulnerability_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    from ..repositories.comment_repository import CommentRepository
    return CommentRepository(db).list_by_vulnerability(vulnerability_id)


@router.post("/vulnerabilidades/{vulnerability_id}/comentarios", response_model=CommentRead, status_code=201)
def create_comment(
    vulnerability_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return VulnerabilityService(db).add_comment(
        vulnerability_id=vulnerability_id,
        author_id=user.id,
        text=payload.text,
    )
