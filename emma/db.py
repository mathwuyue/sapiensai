import datetime
from peewee import *
from playhouse.postgres_ext import PostgresqlExtDatabase, BinaryJSONField
from pgvector.peewee import VectorField
import dotenv
import os
from utils import make_table_name

dotenv.load_dotenv()


db = PostgresqlExtDatabase(
    os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", 19032)
)


class BaseModel(Model):
    class Meta:
        database = db
        table_function = make_table_name


class Document(Model):
    id = AutoField(primary_key=True)
    doc_id = CharField(max_length=255, unique=True)
    filename = CharField(max_length=255)
    organization = CharField(max_length=255, index=True)
    path = CharField(max_length=255, null=True)
    search_privilege = IntegerField(default=100)
    description = TextField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField()
    meta = BinaryJSONField(null=True)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)

    class Meta:
        database = db
        table_function = make_table_name
        indexes = (
            (('filename', 'organization'), False),
        )


class Vector1536(BaseModel):
    id = AutoField(primary_key=True)
    doc_id = CharField(max_length=255, index=True)
    text = TextField()
    embedding = VectorField(dimensions=1536)
    organization = CharField(max_length=255, index=True)
    meta = BinaryJSONField()
        
        
class Vector512(BaseModel):
    id = AutoField(primary_key=True)
    doc_id = CharField(max_length=255, index=True)
    text = TextField()
    embedding = VectorField(dimensions=512)
    organization = CharField(max_length=255, index=True)
    meta = BinaryJSONField()
        
        
class Vector1024(BaseModel):
    id = AutoField(primary_key=True)
    doc_id = CharField(max_length=255, index=True)
    text = TextField()
    embedding = VectorField(dimensions=1024)
    organization = CharField(max_length=255, index=True)
    meta = BinaryJSONField()
        

class Vector2048(BaseModel):
    id = AutoField(primary_key=True)
    doc_id = CharField(max_length=255, index=True)
    text = TextField()
    embedding = VectorField(dimensions=2048)
    organization = CharField(max_length=255, index=True)
    meta = BinaryJSONField()
        
        
class Vector768(BaseModel):
    id = AutoField(primary_key=True)
    doc_id = CharField(max_length=255, index=True)
    text = TextField()
    embedding = VectorField(dimensions=768)
    organization = CharField(max_length=255, index=True)
    meta = BinaryJSONField()
        

class Vector1792(BaseModel):
    id = AutoField(primary_key=True)
    doc_id = CharField(max_length=255, index=True)
    text = TextField()
    embedding = VectorField(dimensions=1792)
    organization = CharField(max_length=255, index=True)
    meta = BinaryJSONField()
        
        
class MemoryModel(Model):
    id = AutoField(primary_key=True)
    text = TextField()
    embedding = VectorField(dimensions=1792)
    ans = TextField()
    organization = CharField(max_length=255, index=True)
    meta = BinaryJSONField()
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)

    class Meta:
        database = db
        table_name = 'emma_memory'
        

class UserHistory(Model):
    id = AutoField(primary_key=True)
    user_id = CharField(max_length=255)
    session_id = UUIDField()
    user_meta = BinaryJSONField(null=True)
    role = CharField(max_length=15)
    message = TextField()
    state = CharField(max_length=15, null=True)
    is_deleted = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
        table_function = make_table_name
        indexes = (
            (('user_id', 'session_id', 'is_deleted'), False),
        )
        
        
if __name__ == '__main__':
    db.connect()
    db.create_tables([Vector1536, Vector512, Vector1024, Vector2048, Vector768, Vector1792, MemoryModel, UserHistory])
    db.close()