from fastapi import FastAPI
import models.todos_model
from database.postgresql import engine
from routers.auth import router as auth
from routers.todo import router as todo
from routers.admin import router as admin
from routers.users import router as users
import pdb

app = FastAPI()

models.todos_model.Base.metadata.create_all(bind=engine)
app.include_router(auth)
app.include_router(todo, prefix="/todo", tags=["todo"])
app.include_router(admin, prefix="/todo", tags=["admin"])
app.include_router(users, prefix="/todo", tags=["users"])
