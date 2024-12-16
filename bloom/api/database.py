from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
#replace later
#DATABASE_URL = "postgresql://user:password@localhost:5432/your_db_name"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sapiens:F5jlkMmD4gQzg+c0GdJ7Qw@115.223.19.227:15432/sapiens_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

        #DATABASE_URL = "postgresql://postgres:F5jlkMmD4gQzg+c0GdJ7Qw@115.223.19.227:15432/sapiens_db"