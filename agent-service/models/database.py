import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, Float
from datetime import datetime
import structlog

logger = structlog.get_logger()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/sentient_playground")

# Convert postgresql:// to postgresql+asyncpg:// for async support and remove sslmode if present
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    # Remove sslmode parameter if present
    if "sslmode=" in DATABASE_URL:
        import re
        DATABASE_URL = re.sub(r'[?&]sslmode=\w+', '', DATABASE_URL)
        DATABASE_URL = DATABASE_URL.rstrip('?&')

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


class UsageLog(Base):
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    user_id = Column(String, nullable=True)
    prompt = Column(Text)
    workflow_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class ApiUsage(Base):
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # Wallet address or 'local'
    job_id = Column(String, index=True)
    provider = Column(String)  # 'openai', 'anthropic', 'fireworks'
    model = Column(String)  # Model name
    tokens_used = Column(Integer, default=0)  # Total tokens
    estimated_cost = Column(Float, default=0.0)  # Estimated cost in USD
    created_at = Column(DateTime, default=datetime.utcnow)


async def init_db():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))


async def get_db():
    """Get database session"""
    async with AsyncSessionLocal() as session:
        yield session
