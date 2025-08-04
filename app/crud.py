from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from . import models, schemas


async def get_user(db: AsyncSession, user_id: int, include_todos: bool = False):
    query = select(models.User)
    if include_todos:
        query = query.options(selectinload(models.User.todos))
    query = query.filter(models.User.id == user_id)
    result = await db.execute(query)
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str, include_todos: bool = False):
    query = select(models.User)
    if include_todos:
        query = query.options(selectinload(models.User.todos))
    query = query.filter(models.User.email == email)
    result = await db.execute(query)
    return result.scalars().first()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100, include_todos: bool = False):
    query = select(models.User)
    if include_todos:
        query = query.options(selectinload(models.User.todos))
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    # After creation, the 'todos' relationship will be empty, so no need to reload.
    return db_user


async def get_todos(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Todo).offset(skip).limit(limit))
    return result.scalars().all()


async def create_user_todo(db: AsyncSession, todo: schemas.TodoCreate, user_id: int):
    try:
        db_todo = models.Todo(**todo.model_dump(), owner_id=user_id)
        db.add(db_todo)
        await db.commit()
        await db.refresh(db_todo)
        return db_todo
    except SQLAlchemyError:
        await db.rollback()
        return None


async def get_todo(db: AsyncSession, todo_id: int):
    result = await db.execute(select(models.Todo).filter(models.Todo.id == todo_id))
    return result.scalars().first()


async def update_todo(db: AsyncSession, todo_id: int, todo: schemas.TodoUpdate):
    db_todo = await get_todo(db, todo_id)
    if db_todo:
        update_data = todo.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_todo, key, value)
        await db.commit()
        await db.refresh(db_todo)
    return db_todo


async def delete_todo(db: AsyncSession, todo_id: int):
    db_todo = await get_todo(db, todo_id)
    if db_todo:
        await db.delete(db_todo)
        await db.commit()
        return True
    return False
