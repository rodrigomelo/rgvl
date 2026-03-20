"""
RGVL Database - SQLAlchemy setup
"""
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Database path — single source of truth
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / 'data' / 'rgvl.db'

# Ensure data directory exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Engine
engine = create_engine(
    f'sqlite:///{DB_PATH}',
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
    echo=False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    """Get a new database session. Caller must close it."""
    return SessionLocal()
