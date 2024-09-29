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


from fastapi import APIRouter

router = APIRouter(
     prefix="/admin",
    tags=["admin"],
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


@router.get("/fetch-all")
async def read_all(user: user_dependency, 
                    db: db_dependency):
    """
    Returns all TODOs in the database.

    This endpoint returns a list of all TODOs in the database. The TODOs are
    returned in the order they were inserted.
    """
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=401, 
                            detail="Authentication Failed")
    return db.query(models.todos_model.Todos).all()


@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(  user: user_dependency, 
                        db: db_dependency, 
                        id: int = Path(gt=0), ):
    """
    Deletes a single TODO from the database.

    This endpoint deletes a single TODO from the database based on the
    `todo_id` parameter. If the TODO is not found, a 404 error is returned.
    """
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=401, 
                            detail="Authentication Failed") 
    todo_model: models.todos_model.Todos = db.query(models.todos_model.Todos) \
                                                .filter(models.todos_model.Todos.id == id).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail="TODO not found")
    db.delete(todo_model)
    db.commit()