import pdb
from fastapi import Depends, HTTPException, Path
from fastapi import status
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import models.todos_model
from models import todos_model
from database.postgresql import SessionLocal
from .auth import get_current_user


from fastapi import APIRouter

router = APIRouter()


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

# create Pydanic request model
class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=40)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    completed: bool = False

@router.get("/read-all")
async def read_all(user: user_dependency, db: db_dependency):
    """
    Returns all TODOs in the database.

    This endpoint returns a list of all TODOs in the database. The TODOs are
    returned in the order they were inserted.
    """
    if user is None:
        raise HTTPException(status_code=401, 
                        detail="Authentication Failed")
    return db.query(models.todos_model.Todos) \
                .filter(models.todos_model.Todos.owner_id == user.get("id")).all()


@router.get("/fetch-all")
async def fetch_all(user: user_dependency, 
                    db: db_dependency):
    """
    Returns all TODOs in the database.

    This endpoint returns a list of all TODOs in the database. The TODOs are
    returned in the order they were inserted.
    """
    if user is None:
        raise HTTPException(status_code=401, 
                            detail="Authentication Failed")
    return db.query(models.todos_model.Todos).all() 


@router.get("/fetch/{id}")
async def read_todo(user: user_dependency, 
                    db: db_dependency, 
                    id: int = Path(gt=0)):
    """
    Returns a single TODO from the database.

    This endpoint returns a single TODO from the database based on the
    `todo_id` parameter. If the TODO is not found, a 404 error is returned. 
    """
    if user is None:
        raise HTTPException(status_code=401, 
                            detail="Authentication Failed")
        
    todo_model: models.todos_model.Todos = db.query(models.todos_model.Todos) \
                .filter(models.todos_model.Todos.id == id) \
                .filter(models.todos_model.Todos.owner_id == user.get("id")) \
                .first()
                
    if not todo_model:
        raise HTTPException(status_code=404, detail="TODO not found")
    return todo_model

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,
                      db: db_dependency, 
                      todo_request: TodoRequest,                       
                      ):
    """
    Creates a new TODO in the database.

    This endpoint creates a new TODO in the database based on the data
    provided in the `todo_request` parameter. The `todo_request` parameter
    must be an instance of the `TodoRequest` model.
    """    
    # user = authenticate_user(form_data.username, form_data.password, db)
    if user is None:
        raise HTTPException(status_code=401, 
                            detail="Authentication Failed")    
    todo_model: models.todos_model.Todos = models.todos_model.Todos(**todo_request.model_dump(), owner_id=user.get("id"))

    db.add(todo_model)
    db.commit()
    return todo_model


@router.put("/update/{id}", status_code=status.HTTP_200_OK)
async def update_todo(user: user_dependency, 
                      todo_request: TodoRequest, 
                      db: db_dependency,
                      id: int = Path(gt=0), ):
    """
    Updates a single TODO in the database.

    This endpoint updates a single TODO in the database based on the
    `todo_id` parameter. If the TODO is not found, a 404 error is returned.
    The `todo_request` parameter must be an instance of the `TodoRequest`
    model.
    """
    if user is None:
        raise HTTPException(status_code=401, 
                            detail="Authentication Failed") 
    todo_model: models.todos_model.Todos = db.query(models.todos_model.Todos) \
                                                .filter(models.todos_model.Todos.id == id).first()
    if not todo_model:
        raise HTTPException(status_code=404, 
                            detail="TODO not found")     
    
    for key, value in todo_request.model_dump().items():
        setattr(todo_model, key, value)   
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model


@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(  user: user_dependency, 
                        db: db_dependency, 
                        id: int = Path(gt=0), ):
    """
    Deletes a single TODO from the database.

    This endpoint deletes a single TODO from the database based on the
    `todo_id` parameter. If the TODO is not found, a 404 error is returned.
    """
    if user is None:
        raise HTTPException(status_code=401, 
                            detail="Authentication Failed") 
    todo_model: models.todos_model.Todos = db.query(models.todos_model.Todos) \
                                                .filter(models.todos_model.Todos.id == id).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail="TODO not found")
    db.delete(todo_model)
    db.commit()