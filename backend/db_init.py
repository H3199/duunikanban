from sqlmodel import SQLModel
from models.schema import *  # ensure models are imported
from core.database import engine


def init_db():
    print("Creating tables if they do not exist...")
    SQLModel.metadata.create_all(engine)
    print("DB initialized!")


if __name__ == "__main__":
    init_db()
