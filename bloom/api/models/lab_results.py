from sqlalchemy import Column, Numeric, String, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship
from ..db.base_class import Base

class LabResults(Base):
    __tablename__ = "bloom_lab_results"

    checkup_id = Column(Integer, ForeignKey("bloom_checkups.id"))
    hemoglobin = Column(Numeric(4, 1))
    blood_glucose = Column(Numeric(4, 1))
    hbsag = Column(String(10))
    hiv = Column(String(10))
    syphilis = Column(String(10))
    tsh = Column(Numeric(5, 2))
    urine_protein = Column(String(10))
    urine_glucose = Column(String(10))
    notes = Column(Text)

    # Relationships
    checkup = relationship("Checkup", back_populates="lab_results")