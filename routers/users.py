import pdb
from fastapi import Depends, HTTPException, Path
from fastapi import status
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import models.todos_model
from models import todos_model
from database.sqlite import SessionLocal
from .auth import get_current_user
from passlib.context import CryptContext
from models.todos_model import Users
from models.users_model import UsersVerification


from fastapi import APIRouter

router = APIRouter(
     prefix="/users",
    tags=["users"],
)

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
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/fetch-all")
async def get_user(user: user_dependency, 
                    db: db_dependency):
    """
    Returns all TODOs in the database.

    This endpoint returns a list of all TODOs in the database. The TODOs are
    returned in the order they were inserted.
    """
    if user is None:
        raise HTTPException(status_code=401, 
                            detail="Authentication Failed")
    return db.query(Users).filter(Users.id == user.get("id")).first()


@router.put("/password", status_code=status.HTTP_200_OK)
async def update_password(user: user_dependency,
                          db: db_dependency,
                          user_verification: UsersVerification):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    pdb.set_trace()
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password): # type: ignore
        raise HTTPException(status_code=401, detail="Error on password change. Please try again")

    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
    return user_model