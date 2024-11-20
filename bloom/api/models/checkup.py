from sqlalchemy import Column, String, Integer, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..db.base_class import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid
class Checkup(Base):
    __tablename__ = "bloom_checkups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("bloom_patients.id"), nullable=False)
    pregnancy_week = Column(Integer)
    checkup_date = Column(Date, nullable=False)
    doctor_id = Column(String(36))
    next_appointment = Column(Date)
    notes = Column(Text)

    # Relationships
    patient = relationship("Patient", back_populates="checkups")
    vital_signs = relationship("VitalSigns", back_populates="checkup", uselist=False)
    ultrasound = relationship("Ultrasound", back_populates="checkup", uselist=False)
    lab_results = relationship("LabResults", back_populates="checkup", uselist=False)
    prenatal_screenings = relationship("PrenatalScreening", back_populates="checkup")
    recommendations = relationship("Recommendation", back_populates="checkup")