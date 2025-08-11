from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True
)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def init_db():
    async with engine.begin() as conn:
        # Aquí podrías agregar await conn.run_sync(Base.metadata.drop_all) en desarrollo
        await conn.run_sync(Base.metadata.create_all)

async def get_session():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
