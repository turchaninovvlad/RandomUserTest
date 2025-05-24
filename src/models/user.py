from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Column, JSON
import sqlalchemy.dialects.sqlite as sqlite

class UserBase(SQLModel):
    gender: str
    name: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    location: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    email: str
    login: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    dob: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    registered: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    phone: str
    cell: str
    picture: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    nat: str


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    external_id: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column("external_id", sqlite.JSON)  # Измените имя столбца
    )

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int

class UserDetailResponse(SQLModel):
    id: int
    gender: str
    full_name: str
    email: str
    phone: str
    location: str
    picture_large: str

#class UserRandomResponse(UserBase):
#    id: int
#    gender: str
#    full_name: str
#    email: str
#    phone: str
#    location: str
#    picture_large: str