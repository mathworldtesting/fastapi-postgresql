from database.postgresql import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from pydantic import BaseModel, Field
from passlib.context import CryptContext


class UsersVerification(BaseModel):
    password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)