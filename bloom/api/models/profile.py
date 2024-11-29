from sqlalchemy import Column, ForeignKey, Float, Integer, String, Text, BigInteger, Boolean
from sqlalchemy.orm import relationship
from api.db.base_class import Base, id_generator

class Profile(Base):
    __tablename__ = "bloom_profiles"

    id = Column(BigInteger, primary_key=True, default=id_generator.generate_id)
    user_id = Column(BigInteger, ForeignKey("bloom_users.id"), nullable=False)
    
    # basic info
    age = Column(Integer, nullable=False)
    pre_weight = Column(Float, nullable=False, comment="pre-pregnancy weight(kg)")
    cur_weight = Column(Float, nullable=False, comment="current weight(kg)")
    height = Column(Float, nullable=False, comment="height(cm)")
    
    # checkup info
    glucose = Column(Float, comment="fasting glucose value(mmol/L)")
    hba1c = Column(Float, comment="HbA1c(%)")
    blood_pressure_high = Column(Integer, comment="blood pressure systolic(mmHg)")
    blood_pressure_low = Column(Integer, comment="blood pressure diastolic(mmHg)")
    
    # pregnancy info
    gestational_age = Column(Integer, nullable=False, comment="gestational age")
    
    # lifestyle
    exercise_level = Column(Integer, comment="exercise level: 1-no exercise, 2-less exercise, 3-regular exercise, 4-heavy exercise")
    
    # medical advice
    prescription = Column(Text, comment="doctor prescription")
    dietary_advice = Column(Text, comment="dietary advice")

    # relationships
    user = relationship("User", back_populates="profile")
    conditions = relationship("UserCondition", back_populates="profile", cascade="all, delete-orphan")
    complications = relationship("UserComplication", back_populates="profile", cascade="all, delete-orphan")

    class Config:
        orm_mode = True

class PresetCondition(Base):
    __tablename__ = "bloom_preset_conditions"

    id = Column(BigInteger, primary_key=True, default=id_generator.generate_id)
    name = Column(String(50), nullable=False, unique=True, comment="preset disease name")
    description = Column(Text, comment="disease description")
    is_active = Column(Boolean, default=True, comment="whether this condition is available for selection")

class UserCondition(Base):
    __tablename__ = "bloom_user_conditions"

    id = Column(BigInteger, primary_key=True, default=id_generator.generate_id)
    profile_id = Column(BigInteger, ForeignKey("bloom_profiles.id"), nullable=False)
    preset_condition_id = Column(BigInteger, ForeignKey("bloom_preset_conditions.id"), nullable=False)
    level = Column(Integer, comment="disease level: 1-mild, 2-moderate, 3-severe")
    
    # relationships
    profile = relationship("Profile", back_populates="conditions")
    preset_condition = relationship("PresetCondition")

class PresetComplication(Base):
    __tablename__ = "bloom_preset_complications"

    id = Column(BigInteger, primary_key=True, default=id_generator.generate_id)
    name = Column(String(50), nullable=False, unique=True, comment="preset complication name")
    description = Column(Text, comment="complication description")
    is_active = Column(Boolean, default=True, comment="whether this complication is available for selection")

class UserComplication(Base):
    __tablename__ = "bloom_user_complications"

    id = Column(BigInteger, primary_key=True, default=id_generator.generate_id)
    profile_id = Column(BigInteger, ForeignKey("bloom_profiles.id"), nullable=False)
    preset_complication_id = Column(BigInteger, ForeignKey("bloom_preset_complications.id"), nullable=False)
    
    # relationships
    profile = relationship("Profile", back_populates="complications")
    preset_complication = relationship("PresetComplication")