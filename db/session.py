from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Укажите URL вашей базы данных PostgreSQL
SQLALCHEMY_DATABASE_URL = 'postgresql+asyncpg://user_art:1324@localhost/articles_db'

# Создайте движок SQLAlchemy
engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

# Создайте фабрику сессий
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


# Функция для получения сессии
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db


# Функция для создания таблиц
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
