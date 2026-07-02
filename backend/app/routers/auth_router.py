from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from ..auth import create_access_token, create_refresh_token, refresh_access_token, revoke_all_user_tokens
from ..core.deps import get_current_user, require_admin
from ..core.logging import get_logger
from ..core.rate_limit import limiter
from ..database import get_db
from ..models import User
from ..schemas import LoginRequest, LoginResponse, RefreshRequest, RefreshResponse, UserCreate, UserRead
from ..services.auth_service import AuthService

logger = get_logger(__name__)
router = APIRouter(tags=["auth"])


@router.post("/auth/login", response_model=LoginResponse)
@limiter.limit("5/minute")
def login(request: Request, payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    result = AuthService(db).login(payload.username, payload.password)
    if not result:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    user = result

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(db, user)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        username=user.username,
        role=user.role.value if hasattr(user.role, "value") else user.role,
    )


@router.post("/auth/refresh", response_model=RefreshResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    result = refresh_access_token(db, payload.refresh_token)
    if not result:
        raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")
    access_token, new_refresh, _user = result
    return RefreshResponse(access_token=access_token, refresh_token=new_refresh)


@router.post("/auth/logout")
def logout(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    revoke_all_user_tokens(db, user.id)
    user.token_version += 1
    db.flush()
    return {"message": "Sesión cerrada"}


@router.get("/auth/me")
def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value if hasattr(user.role, "value") else user.role,
        "active": user.active,
    }
