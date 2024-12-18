import os
import datetime
from peewee import *
from playhouse.postgres_ext import PostgresqlExtDatabase, BinaryJSONField, ArrayField
from dotenv import load_dotenv
from utils import make_table_name


load_dotenv()

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


class User(BaseModel):
    id = AutoField(primary_key=True)
    userid = CharField(unique=True)
    user_meta = BinaryJSONField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField()
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)


def add_user(username, password):
    return User.create(username=username, password=password)


def get_user(username):
    try:
        return User.get(User.username == username)
    except User.DoesNotExist:
        return None
    
    
class UploadFile(BaseModel):
    id = AutoField(primary_key=True)
    doc_id = CharField(unique=True)
    title = CharField(max_length=255)
    filename = CharField(max_length=2047)
    app_id = CharField(max_length=255)
    filetype = CharField(max_length=255)
    type = CharField(max_length=255)
    auth = ArrayField(CharField, null=True)
    meta = BinaryJSONField(null=True)
    status = CharField(max_length=255, default='waiting')
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField()
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)

    class Meta:
        indexes = (
            (('filename', 'app_id'), False),
        )
        

class Product(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField(max_length=255)
    pid = BigIntegerField(unique=True)
    price = DecimalField(max_digits=10, decimal_places=2)
    brief = CharField(max_length=512)
    description = TextField()
    meta = BinaryJSONField(null=True)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)
    
    
# if __name__ == '__main__':
#     from utils import autodiscover_models
#     autodiscover_models(database=db)