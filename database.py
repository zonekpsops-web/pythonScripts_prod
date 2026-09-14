import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Fetch database credentials from environment variables
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")
DB_HOST = os.getenv("DB_HOST", "your-rds-endpoint.amazonaws.com")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")

# PostgreSQL URL using the asyncpg driver
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create an async engine for the database
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a session factory for asynchronous sessions
AsyncSessionLocal = async_sessionmaker(bind=engine, class=AsyncSession, expire_on_commit=False)

Base = declarative_base()

# fastapi dependency to get the database session
async def get_db():
    async with AsyncSessionLocal() as session
        yield session