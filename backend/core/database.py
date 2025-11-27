# backend/core/database.py
from sqlmodel import SQLModel, Session, create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./duunikanban.db")

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    from models.schema import SQLModel  # ensures models are imported
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
