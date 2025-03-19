# sync_database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from .database import Base
import os

load_dotenv()

SYNC_DATABASE_URL = os.getenv("SYNC_DATABASE_URL")

sync_engine = create_engine(SYNC_DATABASE_URL, echo=True, future=True)
SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)

