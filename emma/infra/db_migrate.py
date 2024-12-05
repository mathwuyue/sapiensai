import os
import inspect
from dotenv import load_dotenv
from peewee import Model
from playhouse.postgres_ext import PostgresqlExtDatabase

# Import all models using *
from db import *
from nutrition.db import *
from serve.db import *

def get_all_models():
    """Find all Peewee Model classes in imported modules"""
    models = []
    for name, obj in globals().items():
        if (inspect.isclass(obj) 
            and issubclass(obj, Model) 
            and obj != Model 
            and obj.__name__ != 'BaseModel'):
            models.append(obj)
    return models

def init_database():
    """Initialize database and create tables"""
    try:
        load_dotenv()
        
        db = PostgresqlExtDatabase(
            os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 19032))
        )

        # Get all model classes
        models = get_all_models()
        print(f"Detected models: {[m.__name__ for m in models]}")

        # Create tables
        db.connect()
        db.create_tables(models, safe=True)
        print("Database tables created successfully")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
    finally:
        if not db.is_closed():
            db.close()

if __name__ == "__main__":
    init_database()