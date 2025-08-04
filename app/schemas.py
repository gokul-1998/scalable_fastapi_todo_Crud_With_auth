from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import List, Optional


class TodoBase(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    is_done: bool = False


class TodoCreate(TodoBase):
    pass


class Todo(TodoBase):
    id: int
    is_done: bool
    owner_id: int

    model_config = ConfigDict(from_attributes=True)


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_done: Optional[bool] = None


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    model_config = ConfigDict(from_attributes=True)


class User(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserWithTodos(User):
    todos: List[Todo]
