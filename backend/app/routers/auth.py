"""Authentication endpoints.

Two independent account types share this router:

* ``/auth/student/*`` — public student sign-up and sign-in. Any student may
  create an account; the password is hashed and stored in the database.
* ``/auth/*`` — college staff (admin) sign-in. Staff accounts are created from
  configuration/environment, never through a public sign-up form.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Admin, Student
from ..schemas import (
    AdminLogin,
    AdminOut,
    AuthToken,
    StudentLogin,
    StudentOut,
    StudentSignup,
    Token,
)
from ..security import (
    create_access_token,
    get_current_admin,
    get_current_student,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _authenticate(db: Session, email: str, password: str) -> Admin:
    admin = db.scalar(select(Admin).where(func.lower(Admin.email) == email.strip().lower()))
    if admin is None or not verify_password(password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled"
        )
    return admin


# ---------------------------------------------------------------------------
# Students (public)
# ---------------------------------------------------------------------------
@router.post(
    "/student/signup", response_model=AuthToken, status_code=status.HTTP_201_CREATED
)
def student_signup(payload: StudentSignup, db: Session = Depends(get_db)) -> AuthToken:
    email = payload.email.lower().strip()
    existing = db.scalar(select(Student).where(func.lower(Student.email) == email))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    student = Student(
        email=email,
        full_name=payload.full_name.strip(),
        hashed_password=hash_password(payload.password),
        programme=(payload.programme or "").strip() or None,
        semester=(payload.semester or "").strip() or None,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return AuthToken(
        access_token=create_access_token(student.email, "student"),
        account=StudentOut.model_validate(student),
    )


@router.post("/student/login", response_model=AuthToken)
def student_login(payload: StudentLogin, db: Session = Depends(get_db)) -> AuthToken:
    email = payload.email.lower().strip()
    student = db.scalar(select(Student).where(func.lower(Student.email) == email))
    if student is None or not verify_password(payload.password, student.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not student.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled"
        )
    return AuthToken(
        access_token=create_access_token(student.email, "student"),
        account=StudentOut.model_validate(student),
    )


@router.get("/student/me", response_model=StudentOut)
def student_me(student: Student = Depends(get_current_student)) -> Student:
    return student


# ---------------------------------------------------------------------------
# Staff (admin)
# ---------------------------------------------------------------------------
@router.post("/login", response_model=Token)
def login(payload: AdminLogin, db: Session = Depends(get_db)) -> Token:
    admin = _authenticate(db, payload.email, payload.password)
    return Token(access_token=create_access_token(admin.email, admin.role))


@router.post("/token", response_model=Token)
def login_form(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Token:
    """OAuth2 password-flow variant (used by the API docs "Authorize" button)."""
    admin = _authenticate(db, form.username, form.password)
    return Token(access_token=create_access_token(admin.email, admin.role))


@router.get("/me", response_model=AdminOut)
def me(admin: Admin = Depends(get_current_admin)) -> Admin:
    return admin
