from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.deps import require_admin
from ..core.exceptions import BusinessRuleError, ResourceNotFoundError
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


@router.post("/usuarios", response_model=UserRead, status_code=201)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_admin),
):
    if payload.password == "123":
        raise BusinessRuleError("La contraseña debe tener al menos 6 caracteres y no puede ser '123'")
    return UserService(db).create_user(
        username=payload.username,
        email=payload.email,
        role=payload.role.value if hasattr(payload.role, "value") else payload.role,
        password=payload.password,
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
        raise ResourceNotFoundError("Usuario no encontrado")
    return result
