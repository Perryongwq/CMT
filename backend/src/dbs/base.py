# database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database URL, for SQLite it will be a file on your local filesystem
DATABASE_URL = "sqlite:///training_history.db"

# Create a database engine
engine = create_engine(DATABASE_URL, echo=True)

# Base class for your models
Base = declarative_base()

# Session maker for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Import models
    from db import models
    # Create tables
    Base.metadata.create_all(bind=engine)
