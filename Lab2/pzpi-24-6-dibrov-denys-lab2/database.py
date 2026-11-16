from dotenv import load_dotenv
import os
from pathlib import Path

from sqlalchemy import URL, create_engine, text 
from sqlalchemy.orm import DeclarativeBase, sessionmaker


load_dotenv()



database_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME", "dronecare_db"),
)

engine = create_engine(database_url, pool_pre_ping=True)

def check_database_connection():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database()")
        )
        return result.scalar_one()

#базовий клас для всіх моделей
class Base(DeclarativeBase):
    pass

#фабрика сесій 
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit = False,
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()