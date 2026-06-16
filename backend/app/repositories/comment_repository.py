from typing import Optional

from sqlalchemy.orm import Session

from ..models import Comment


class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_vulnerability(self, vulnerability_id: Optional[int] = None) -> list[Comment]:
        query = self.db.query(Comment)
        if vulnerability_id:
            query = query.filter(Comment.vulnerability_id == vulnerability_id)
        return query.order_by(Comment.created_at.asc()).all()

    def create(self, **kwargs) -> Comment:
        comment = Comment(**kwargs)
        self.db.add(comment)
        self.db.flush()
        return comment
