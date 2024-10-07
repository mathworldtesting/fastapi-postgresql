from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database.postgresql import SessionLocal
from models.todos_model import Users
from sqlalchemy.orm import Session
from fastapi import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import pdb
from jose import jwt, JWTError
from fastapi import status

router = APIRouter(
    prefix="/todo",
    tags=["authorization"],
)

SECRET_KEY = '1dfda60e85211ce3a30ce7d0dbc9ad634d2a9333afa4b73d3c98452e2b9898a5'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/todo/login")


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    user_role: str
    
class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    """
    Yields a database session object.

    This function is meant to be used as a FastAPI dependency. It yields a
    database session object that can be used to query the database. The
    session is automatically closed when the context manager is exited.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    """
    Creates a JSON Web Token for the given username and user ID.

    This function creates a JSON Web Token that can be used to authenticate
    a user. The token contains the username and user ID, and is valid for a
    specified period of time given by the `expires_delta` parameter.

    :param username: The username of the user
    :param user_id: The user ID of the user
    :param expires_delta: The timedelta during which the token is valid
    :return: A JSON Web Token
    """
    encode = {"sub": username, "id": user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:   
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")
        user_role = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail="Cound not validate user credentials")
        return {"username": username, "id": user_id, "role": user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail="Cound not validate user credentials")
    

@router.post("/user/register", status_code=status.HTTP_201_CREATED)
async def register_users(db: db_dependency, 
                       create_user_request: CreateUserRequest) -> dict:
    """
    Creates a new user in the database.

    This endpoint creates a new user in the database based on the data
    provided in the `create_user_request` parameter. The `create_user_request`
    parameter must be an instance of the `CreateUserRequest` model.
    """
    create_user_model = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        role = create_user_request.user_role,        
        is_active = True                
    )        
    db.add(create_user_model)
    db.commit()   
    return {"message": "User created"}

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                db : db_dependency):           
    """
    Returns a JSON Web Token for the given username and password.

    This endpoint is meant to be used with a HTML form, where the username and
    password are provided in the form data. The username and password are
    verified against the users in the database. If the credentials are valid,
    a JSON Web Token is returned.

    :param form_data: The form data containing the username and password
    :param db: The database session
    :return: A JSON Web Token if the credentials are valid
    """
    user = authenticate_user(form_data.username, form_data.password, db)    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail="Cound not validate user credentials")
    token = create_access_token(form_data.username, user.id, user.role, timedelta(minutes=20)) # type: ignore
    
    return { "access_token": token, 
            "token_type": "bearer", 
            "message": "Successful Authentication" }

def authenticate_user(username: str, password: str, db) -> bool:
    """
    Authenticates a user against the database.

    This function authenticates a user given the username and password. It
    will return True if the user is authenticated and False if the user is
    not authenticated.

    :param username: The username of the user
    :param password: The password of the user
    :param db: The database session
    :return: True if the user is authenticated, False otherwise
    """        
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user