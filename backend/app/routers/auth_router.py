from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas import UserCreate, UserPrivate, Token
from app.auth import (
    hash_password,
    verify_and_update_password,
    create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
def signup(body: UserCreate, db: Annotated[Session, Depends(get_db)]):
    existing = db.execute(
        select(models.User).where(models.User.email == body.email)
    ).scalars().first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = models.User(
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.fullname,  # confirm this matches your models.User column name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    user = db.execute(
        select(models.User).where(models.User.email == form_data.username)
    ).scalars().first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    is_valid, new_hash = verify_and_update_password(form_data.password, user.hashed_password)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    # Opportunistic upgrade: old bcrypt hashes -> argon2
    if new_hash is not None:
        user.hashed_password = new_hash
        db.commit()

    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserPrivate)
def read_current_user(current_user: Annotated[models.User, Depends(get_current_user)]):
    return current_user


@router.get("/users/{user_id}", response_model=UserPrivate)
def get_user(user_id: UUID, db: Annotated[Session, Depends(get_db)]):
    user = db.execute(
        select(models.User).where(models.User.id == user_id)
    ).scalars().first()

    if user:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")