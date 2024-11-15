from sqlalchemy import Boolean, Column, String
from ..db.base_class import Base

class User(Base):
    __tablename__ = "bloom_users"

    id = None
    user_id = Column(String(36), primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)