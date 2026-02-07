
from quopri import encode
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException,status,Request, Header, Cookie
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session


from datetime import timedelta, datetime, timezone
from ..database import SessionLocal
from ..models import Users
from  passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates
router= APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = "d761a848bcec94d7a6a61da010e8e7b9d396c28124d0ce44c67e10247d0d83c7"
ALGORITHM = "HS256"
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

class CreateUserRequest(BaseModel):
    email: str = Field(..., example="user@example.com")
    username: str = Field(..., example="johndoe")
    first_name: str = Field(..., example="John")
    last_name: str = Field(..., example="Doe")
    password: str = Field(..., example="password")
    role: str = Field(..., example="user")

class Token(BaseModel):
    access_token: str
    token_type: str
    
def get_db():
    db = SessionLocal() # create a new database session
    try:
        yield db # yield the session to be used in the path operation
    finally:
        db.close()



db_dependency = Annotated[Session, Depends(get_db)]
templates = Jinja2Templates(directory="Todoapp/templates")



##pages ###
@router.get("/login-page", status_code=status.HTTP_200_OK)
def render_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register-page", status_code=status.HTTP_200_OK)
def render_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

##Endpoints ###

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username:str,user_id:int,role:str,expires_delta: timedelta = timedelta(minutes=15)):
    to_encode = {"sub": username, "user_id": user_id, "role": role}
    expires=datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expires})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_token_from_request(
    header_token: str | None = Depends(oauth2_bearer),   # ✅ enables Swagger Authorize
    access_token: str | None = Cookie(default=None),     # ✅ enables browser cookie auth
) -> str | None:
    # 1) If Swagger/API sends Authorization: Bearer <token>
    if header_token:
        return header_token

    # 2) Else fallback to cookie from browser
    return access_token


async def get_current_user(
    token: str | None = Depends(get_token_from_request),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")

        if username is None or user_id is None or role is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(Users).filter(Users.username == username).first()
    if user is None:
        raise credentials_exception

    return user


@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: CreateUserRequest, db: db_dependency):
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        role=create_user_request.role,
        is_active=True
    )
    db.add(create_user_model)
    db.commit()

    ##jwt token
    
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
        user= authenticate_user(db, form_data.username, form_data.password)
        if not user:
              raise HTTPException(status_code=401, detail="Invalid username or password")
        
        token= create_access_token(user.username, user.id, user.role, timedelta(minutes=30)    )
        return {"access_token": token, "token_type": "bearer"}