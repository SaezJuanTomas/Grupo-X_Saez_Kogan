import uuid
from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .core.config import config
from .models import RefreshToken, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "role": user.role.value if hasattr(user.role, "value") else user.role,
        "type": "access",
        "ver": user.token_version,
        "exp": datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)


def create_refresh_token(db: Session, user: User) -> str:
    jti = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user.id),
        "jti": jti,
        "type": "refresh",
        "exp": expires_at,
    }
    token_str = jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)

    db.add(RefreshToken(jti=jti, user_id=user.id, expires_at=expires_at))
    db.flush()
    return token_str


def refresh_access_token(db: Session, refresh_token_str: str) -> tuple[str, str, User] | None:
    try:
        payload = jwt.decode(refresh_token_str, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        jti = payload.get("jti")
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        return None

    stored = db.query(RefreshToken).filter(
        RefreshToken.jti == jti,
        RefreshToken.revoked == False,
        RefreshToken.expires_at > datetime.utcnow(),
    ).first()
    if not stored:
        return None

    stored.revoked = True
    db.flush()

    user = db.query(User).filter(User.id == user_id, User.active == True).first()
    if not user:
        return None

    new_access = create_access_token(user)
    new_refresh = create_refresh_token(db, user)
    db.flush()
    return new_access, new_refresh, user


def revoke_all_user_tokens(db: Session, user_id: int) -> None:
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked == False,
    ).update({"revoked": True})
    db.flush()
