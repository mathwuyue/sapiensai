from sqlalchemy import Column, String, Integer, Date, Text, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from api.db.base_class import Base, id_generator

class Checkup(Base):
    __tablename__ = "bloom_checkups"

    id = Column(BigInteger, primary_key=True, index=True, default=id_generator.generate_id)
    user_id = Column(BigInteger, ForeignKey("bloom_users.id"), nullable=False)
    pregnancy_week = Column(Integer)
    checkup_date = Column(Date, nullable=False)
    doctor_id = Column(String(36))
    next_appointment = Column(Date)
    notes = Column(Text)

    # Relationships
    user = relationship("User", back_populates="checkups")
    vital_signs = relationship("VitalSigns", back_populates="checkup", uselist=False)
    ultrasound = relationship("Ultrasound", back_populates="checkup", uselist=False)
    lab_results = relationship("LabResults", back_populates="checkup", uselist=False)
    prenatal_screenings = relationship("PrenatalScreening", back_populates="checkup")
    recommendations = relationship("Recommendation", back_populates="checkup")