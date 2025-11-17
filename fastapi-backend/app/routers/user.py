from hashlib import sha256
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.user import UserCreate, UserRead

router = APIRouter()


def _hash_password(raw_password: str) -> str:
    return sha256(raw_password.encode("utf-8")).hexdigest()


@router.get("/", response_model=List[UserRead])
def list_users(db: Session = Depends(get_db)) -> List[User]:
    return db.query(User).all()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")

    new_user = User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=_hash_password(payload.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

