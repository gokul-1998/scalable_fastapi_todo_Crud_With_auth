from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@db:5432/appdb")

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,  # Number of connections to keep open in the pool
    max_overflow=20,  # Number of connections that can be opened beyond the pool_size
)

AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
