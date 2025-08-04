from contextlib import asynccontextmanager
from typing import List, Union
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, models, schemas
from .database import engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.create_user(db=db, user=user)


@app.get("/users/")
async def read_users(
    skip: int = 0, limit: int = 100, include_todos: bool = False, db: AsyncSession = Depends(get_db)
):
    users = await crud.get_users(db, skip=skip, limit=limit, include_todos=include_todos)
    if include_todos:
        return [schemas.UserWithTodos.model_validate(user).model_dump() for user in users]
    return [schemas.User.model_validate(user).model_dump() for user in users]


@app.get("/users/{user_id}")
async def read_user(user_id: int, include_todos: bool = False, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user(db, user_id=user_id, include_todos=include_todos)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if include_todos:
        return schemas.UserWithTodos.model_validate(db_user).model_dump()
    return schemas.User.model_validate(db_user).model_dump()


@app.post("/users/{user_id}/todos/", response_model=schemas.Todo)
async def create_todo_for_user(
    user_id: int, todo: schemas.TodoCreate, db: AsyncSession = Depends(get_db)
):
    db_user = await crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_todo = await crud.create_user_todo(db=db, todo=todo, user_id=user_id)
    if db_todo is None:
        raise HTTPException(status_code=400, detail="Could not create todo.")
    return db_todo


@app.get("/todos/", response_model=list[schemas.Todo])
async def read_todos(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    todos = await crud.get_todos(db, skip=skip, limit=limit)
    return todos


@app.get("/todos/{todo_id}", response_model=schemas.Todo)
async def read_todo(todo_id: int, db: AsyncSession = Depends(get_db)):
    db_todo = await crud.get_todo(db, todo_id=todo_id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo


@app.patch("/todos/{todo_id}", response_model=schemas.Todo)
async def update_todo(
    todo_id: int, todo: schemas.TodoUpdate, db: AsyncSession = Depends(get_db)
):
    db_todo = await crud.update_todo(db, todo_id=todo_id, todo=todo)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo


@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud.delete_todo(db, todo_id=todo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"detail": "Todo deleted successfully"}
