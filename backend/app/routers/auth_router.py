from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, FastAPI

from datetime import timedelta
from pydantic import BaseModel

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.schemas import  UserCreate, UserResponse

from app.database import Base, engine, get_db
import app.models

from app.auth import hash_password

router = APIRouter()

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(body: UserCreate, db: Session = Depends(get_db)):
    existing = db.execute(
        select(app.models.User).where(app.models.User.email == body.email)
    ).scalars().first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_user = app.models.User(
        email           = body.email,
        hashed_password = hash_password(body.password),   # ← the missing piece
        fullname       = body.fullname,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user










# app = FastAPI()


# @app.post("/api/users", response_model=UserResponse)
# def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):  #user  -> request body Usercreate -> a body validator from pydantic
#     result  =  db.execute(
#         select(app.models.User).where(app.models.User.username == user.username),
#     )
#     existing_user  = result.scalars().first()
#     if existing_user:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Username already exists"
#         )
    
#     result  =  db.execute(
#         select(app.models.User).where(app.models.User.email == user.email),
#     )
#     existing_email  = result.scalars().first()
#     if existing_email:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Username already exists"
#         )
    
#     new_user = app.models.User(
#         username = user.username,
#         email = user.email,
#     )

#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)

#     return new_user

# @app.get("/api/users/{user_id}", response_model=UserResponse)
# def get_user(user_id: int,  db: Annotated[Session, Depends(get_db)]):
#     result  =  db.execute(
#         select(app.models.User).where(app.models.User.id == user_id),
#     )
#     user  = result.scalars().first()

#     if user:
#         return user
    
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    




# app.include_router(sms_router.router)

