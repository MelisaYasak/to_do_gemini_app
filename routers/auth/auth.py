from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from passlib.context import CryptContext
from db import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from models.m_user.user import User
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/auth", tags=["Authentication"])

templates = Jinja2Templates(directory="frontend/templates")
SECRET_KEY = "36oE2dqIE8zoxk2axcSrB0KRNl7ccVoN"
ALGORITHM = "HS256"

@router.get("/")
async def hi_auth():
    return {"message": "Hello, Auth!"}

# password with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# when a request is sent to /auth/token, the login_for_access_token method return a token
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")
# for login post, create user request class
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str

class Token(BaseModel):
    access_token: str
    token_type: str

# User authentication
def auth_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
        #raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

# create token
# user_id is the id value of that user we found in the db
# ‘expires_delta’ describes how long this ‘token’ will be invalid.
def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    # payload is mention to payload section. We write in there what we want to use after decode the token. 
    payload = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    payload.update({'exp': expires})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)] ):
    # In todo.py, we control the user by using this method as Depends.     
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        # for security, you should check jwt
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        return {'username': username, 'id': user_id, 'role': role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


#use SessionMaker in db.py with SessionLocal to connect database
def get_db():
    db = SessionLocal()
    try:
        # It is similar to return in that it returns something from the function.
        # But functions using ‘yeild’ are called ‘Generater Function’.
        # While ‘return’ returns a single value, ‘yeild’ can return successive values. You can iterrate into the method.
        yield db
    finally:
        # to close Session
        db.close()
# From now, all methods to be written will ‘depends’ on this method.
db_dependency = Annotated[Session, Depends(get_db)]

#bind frontend login page with backend
@router.get("/login-page")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

#bind frontend register page with backend
@router.get("/register-page")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/")
async def read_all(db: db_dependency):
    return db.query(User).all()

@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, request: CreateUserRequest):
    # new user
    user = User(
        username=request.username, 
        email=request.email, 
        first_name=request.first_name,
        last_name=request.last_name, 
        hashed_password=pwd_context.hash(request.password), 
        role=request.role,
        is_active=True,
        phone_number = request.phone_number
        )
    
    db.add(user)
    db.commit()


# for return a token
@router.post("/token", response_model=Token)
async def login_for_access_token(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = auth_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=60))
    return {"access_token": token, "token_type": "bearer"}


