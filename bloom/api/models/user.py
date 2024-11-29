from sqlalchemy import Boolean, Column, String, BigInteger
from sqlalchemy.orm import relationship
from api.db.base_class import Base, id_generator

class User(Base):
    __tablename__ = "bloom_users"

    id = Column(BigInteger, primary_key=True, index=True, default=id_generator.generate_id)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Relationships
    glucose = relationship("Glucose", back_populates="user")
    profile = relationship("Profile", back_populates="user")
    patients = relationship("Patient", back_populates="user")
    checkups = relationship("Checkup", back_populates="user")