import os
import importlib
import inspect
from peewee import *
from nutrition.db import BaseModel as NDBModel
from serve.db import BaseModel as SDBModel
from db import BaseModel as FDBModel
from playhouse.postgres_ext import PostgresqlExtDatabase


def autodiscover_models(db, module_path='db.py'):
    """
    Automatically discover and create all Peewee model tables
    
    Args:
        db: Peewee database connection
        module_path: Path to the module containing model definitions
    """
    # Ensure the module can be imported
    spec = importlib.util.spec_from_file_location("db_models", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Collect all model classes
    models = [
        obj for name, obj in inspect.getmembers(module) 
        if (inspect.isclass(obj) and 
            issubclass(obj, Model) and 
            obj is not Model and 
            obj is not NDBModel and obj is not SDBModel and obj is not FDBModel)
    ]
    # Create tables
    with db:
        db.create_tables(models)
    
    print(f"Created {len(models)} tables:")
    for model in models:
        print(f" - {model._meta.table_name}")
            

def create_all_tables():
    # Create database connection
    db = PostgresqlExtDatabase(
        os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 19032)
    )
    # Autodiscover and create tables
    autodiscover_models(db, 'nutrition/db.py')
    autodiscover_models(db, 'serve/db.py')
    autodiscover_models(db, 'db.py')

if __name__ == "__main__":
    create_all_tables()