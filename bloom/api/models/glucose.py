from sqlalchemy import Column, ForeignKey, Float, Date, Integer, BigInteger
from sqlalchemy.orm import relationship
from api.db.base_class import Base, id_generator

class Glucose(Base):
    __tablename__ = "bloom_glucose"

    id = Column(BigInteger, primary_key=True, index=True, default=id_generator.generate_id)
    user_id = Column(BigInteger, ForeignKey("bloom_users.id"), nullable=False)
    glucose_value = Column(Float, nullable=False)
    glucose_date = Column(Date, nullable=False)
    measurement_type = Column(Integer, nullable=False, comment="type from 1 to 8, representing breakfast before meal, breakfast after meal (2h), lunch before meal, lunch after meal (2h), dinner before meal, dinner after meal (2h), bedtime (around 22-23), midnight (2am)")

    # Relationships
    user = relationship("User", back_populates="glucose")
