from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_current_user, require_admin
from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserRead, UserUpdate
from ..services.user_service import UserService

router = APIRouter(tags=["users"])


@router.get("/usuarios", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    _user: User = Depends(require_admin),
):
    return UserService(db).list_users()


@router.post("/usuarios", response_model=UserRead)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_admin),
):
    created = UserService(db).create_user(
        username=payload.username,
        email=payload.email,
        role=payload.role,
        password=payload.password,
    )
    return UserRead(
        id=created.id,
        username=created.username,
        email=created.email,
        role=created.role,
        active=created.active,
        latest_activity=created.latest_activity,
        assigned_vulnerabilities=0,
    )


@router.patch("/usuarios/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_admin),
):
    result = UserService(db).update_user(user_id, payload.model_dump(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result
