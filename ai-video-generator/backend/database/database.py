import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from contextlib import asynccontextmanager

from models.database import Base
from utils.config import get_settings

logger = logging.getLogger(__name__)

# Global variables
async_engine = None
async_session_factory = None
sync_engine = None
sync_session_factory = None


async def init_database():
    """Initialize database connection and create tables"""
    global async_engine, async_session_factory, sync_engine, sync_session_factory
    
    settings = get_settings()
    
    if not settings.DATABASE_URL:
        logger.warning("DATABASE_URL not configured, using SQLite")
        # Fallback to SQLite for development
        async_database_url = "sqlite+aiosqlite:///./ai_video.db"
        sync_database_url = "sqlite:///./ai_video.db"
    else:
        # Use PostgreSQL for production
        async_database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        sync_database_url = settings.DATABASE_URL
    
    # Create async engine
    async_engine = create_async_engine(
        async_database_url,
        echo=settings.DEBUG,
        future=True,
        pool_pre_ping=True,
        pool_recycle=300
    )
    
    # Create async session factory
    async_session_factory = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # Create sync engine for migrations
    sync_engine = create_engine(
        sync_database_url,
        echo=settings.DEBUG,
        future=True,
        pool_pre_ping=True,
        pool_recycle=300
    )
    
    # Create sync session factory
    sync_session_factory = sessionmaker(
        bind=sync_engine,
        future=True
    )
    
    # Create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database initialized successfully")


@asynccontextmanager
async def get_async_session():
    """Get async database session"""
    if not async_session_factory:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


def get_sync_session():
    """Get sync database session (for migrations)"""
    if not sync_session_factory:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    return sync_session_factory()


async def close_database():
    """Close database connections"""
    global async_engine, sync_engine
    
    if async_engine:
        await async_engine.dispose()
        async_engine = None
    
    if sync_engine:
        sync_engine.dispose()
        sync_engine = None
    
    logger.info("Database connections closed")


async def check_database_connection():
    """Check if database connection is working"""
    try:
        async with get_async_session() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False


# Database dependency for FastAPI
async def get_db():
    """FastAPI dependency for database session"""
    if not async_session_factory:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    session = async_session_factory()
    try:
        yield session
    finally:
        await session.close()
