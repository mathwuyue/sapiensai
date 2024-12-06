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
        
    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)
        
        
class MealData(BaseModel):
    id = AutoField(primary_key=True)
    userid = CharField(max_length=255)
    type = IntegerField()
    url = BinaryJSONField()
    nutrient = BinaryJSONField()
    emma = BinaryJSONField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField()
    

class FoodDatabase(BaseModel):
    id = AutoField(primary_key=True)
    foodid = CharField(max_length=255)
    url = CharField(max_length=2047, null=True)
    nutrient = BinaryJSONField()
    meta = BinaryJSONField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField()
    

class ExerciseData(BaseModel):
    id = AutoField(primary_key=True)
    user_id = CharField(max_length=255, index=True)
    exercise = CharField(max_length=255, index=True)
    duration = FloatField()
    calories = FloatField()
    remark = CharField(max_length=255, null=True)
    start_time = DateTimeField(null=True)
    emma = BinaryJSONField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField()
    
    
class ExerciseDatabase(BaseModel):
    id = AutoField(primary_key=True)
    exercise = CharField(max_length=255, index=True)
    url = CharField(max_length=2047, null=True)
    calories = FloatField()
    type = CharField(max_length=255, index=True)
    meta = BinaryJSONField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField()
    
    
class Emma(BaseModel):
    id = AutoField(primary_key=True)
    userid = CharField(max_length=255)
    comment = TextField()
    advice = TextField(null=True)
    tables = BinaryJSONField(null=True)
    charts = BinaryJSONField(null=True)
    type = IntegerField()   # 1: food, 2: excersice 3: dietary
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField()
    
    
class UserNutrition(BaseModel):
    id = AutoField(primary_key=True)
    userid = CharField(max_length=255)
    macro = BinaryJSONField()
    micro = BinaryJSONField()
    mineral = BinaryJSONField()
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField()
    
    
class DietaryData(BaseModel):
    id = AutoField(primary_key=True)
    userid = CharField(max_length=255)
    days = IntegerField()
    dietary = BinaryJSONField()
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField()
    
    
class UserPreference(BaseModel):
    """tblname: """
    id = AutoField(primary_key=True)
    userid = CharField(max_length=255)
    appetite = IntegerField(null=True)
    preference = BinaryJSONField()
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField()
    
    
if __name__ == '__main__':
    db.create_tables([MealData, FoodDatabase, ExerciseData, ExerciseDatabase, Emma, DietaryData])