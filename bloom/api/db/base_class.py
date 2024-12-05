from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from sqlalchemy import Column, DateTime, BigInteger
from api.utils.snowflake import Snowflake

id_generator = Snowflake(worker_id=1, datacenter_id=1)

class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id = Column(BigInteger, primary_key=True, index=True, default=id_generator.generate_id)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)