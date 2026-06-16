from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import User
from ..schemas import LoginRequest, LoginResponse
from ..services.auth_service import AuthService

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    result = AuthService(db).login(payload.username, payload.password)
    if not result:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    token, user = result
    return LoginResponse(access_token=token, user_id=user.id, username=user.username, role=user.role)


@router.post("/logout")
def logout(_user: User = Depends(get_current_user)):
    return {"message": "Sesión cerrada"}
