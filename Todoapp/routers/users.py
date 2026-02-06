from typing import Annotated
from fastapi import APIRouter, FastAPI, Depends, HTTPException, Path, Response, status
from pydantic import BaseModel, Field
from ..database import SessionLocal, engine
from ..models import Users
from sqlalchemy.orm import Session
from Todoapp.routers import auth
from .auth import get_current_user
from passlib.context import CryptContext
from Todoapp import models
router = APIRouter()

## create the database

router= APIRouter(
    prefix="/user",
    tags=["user"]
)

def get_db():
    db = SessionLocal() # create a new database session
    try:
        yield db # yield the session to be used in the path operation
    finally:
        db.close()



db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[auth.Users, Depends(get_current_user)]
bycrpt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserVerificationRequest(BaseModel):
    password: str = Field(..., example="your_password_here")
    new_password: str = Field(..., example="your_new_password_here")

@router.get("/",status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid user")
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return db.query(models.Users).filter(models.Users.id == user.id).first()
    
@router.put("/user/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, request: UserVerificationRequest):
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid user")
    if not bycrpt_context.verify(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")
    user_model = db.query(models.Users).filter(models.Users.id == user.id).first()

    if  bycrpt_context.verify(request.new_password, user_model.hashed_password):
          raise HTTPException(status_code=400, detail="New password cannot be the same as the old password")
    user_model.hashed_password = bycrpt_context.hash(request.new_password)
    db.add(user_model)
    db.commit()