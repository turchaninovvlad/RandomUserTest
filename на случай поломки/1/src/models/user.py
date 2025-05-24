from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import BaseModel

class UserBase(SQLModel):
    gender: str
    first_name: str
    last_name: str 
    email: str
    phone: str
    location: str
    picture_thumbnail: str

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class UserCreate(UserBase):
    pass

class UserResponse(BaseModel):
    id: int
    gender: str
    first_name: str
    last_name: str
    email: str
    phone: str
    location: str
    picture_thumbnail: str

class UserRandomResponse(BaseModel):
    id: int
    gender: str
    full_name: str
    email: str
    phone: str
    location: str
    picture_large: str