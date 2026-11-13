"""Authentication, password hashing and role checks."""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import Admin, Student

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def _decode_identity(token: str | None) -> tuple[str, str] | None:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
    subject, role = payload.get('sub'), payload.get('role')
    if not isinstance(subject, str) or not isinstance(role, str):
        return None
    return subject, role


def get_current_admin(
    token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Admin:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    identity = _decode_identity(token)
    if not identity or identity[1] not in {'admin', 'publisher', 'viewer'}:
        raise credentials_error
    email, token_role = identity

    admin = db.scalar(select(Admin).where(Admin.email == email))
    if admin is None or not admin.is_active or admin.role != token_role:
        raise credentials_error
    return admin


def get_current_student(
    token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Student:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    identity = _decode_identity(token)
    if not identity or identity[1] != 'student':
        raise credentials_error
    email, _ = identity

    student = db.scalar(select(Student).where(Student.email == email))
    if student is None or not student.is_active:
        raise credentials_error
    return student


def require_publisher(admin: Admin = Depends(get_current_admin)) -> Admin:
    """Only roles that may upload/publish documents pass this check."""
    if admin.role not in {"admin", "publisher"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires publisher permissions.",
        )
    return admin
