from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings
from app.core.logging import logger
from app.infrastructure.database.models import Base

# Setup database async engine (supports pool recycle for production stability)
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    pool_recycle=1800,
)

# Async session factory
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency yielding an asynchronous SQLAlchemy database session.
    Automatically commits or rolls back operations.
    """
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Transaction failed. Rolling back database changes: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initializes database tables by creating metadata schemas.
    To be used inside test setup routines or initialization scripts.
    """
    try:
        async with engine.begin() as conn:
            # Under SQLite, foreign key support needs explicit enabling
            if "sqlite" in settings.SQLALCHEMY_DATABASE_URI:
                await conn.exec_driver_sql("PRAGMA foreign_keys = ON;")
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schemas initialized successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize database: {str(e)}")
        raise
