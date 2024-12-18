from sqlalchemy import Text,Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Exercise(Base):  # 只声明一次
    __tablename__ = 'emma_exercisedata'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    exercise = Column(String)
    duration = Column(Integer)
    calories = Column(Float)
    intensity = Column(String)
    bpm = Column(Integer)
    remark = Column(String)
    start_time = Column(DateTime)
    emma = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    emma = Column(Text)  # 确保这个字段存在
    #summary = Column(Text, nullable=True)  # 添加 summary
    #advice = Column(Text, nullable=True)