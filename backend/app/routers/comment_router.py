from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import User
from ..repositories.comment_repository import CommentRepository
from ..repositories.history_repository import HistoryRepository
from ..schemas import CommentCreate, CommentRead

router = APIRouter(tags=["comments"])


@router.get("/comentarios", response_model=list[CommentRead])
def list_comments(
    vulnerability_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return CommentRepository(db).list_by_vulnerability(vulnerability_id)


@router.post("/vulnerabilidades/{vulnerability_id}/comentarios", response_model=CommentRead)
def create_comment(
    vulnerability_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    if payload.vulnerability_id != vulnerability_id:
        raise HTTPException(status_code=400, detail="Vulnerability mismatch")

    comment = CommentRepository(db).create(**payload.model_dump())
    HistoryRepository(db).create(
        vulnerability_id=vulnerability_id,
        actor_id=payload.author_id,
        action="Comentario agregado",
        detail="Comentario agregado",
    )
    return comment
