from sqlalchemy import Column, Numeric, String, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from api.db.base_class import Base, id_generator

class LabResults(Base):
    __tablename__ = "bloom_lab_results"

    id = Column(BigInteger, primary_key=True, index=True, default=id_generator.generate_id)
    checkup_id = Column(BigInteger, ForeignKey("bloom_checkups.id"), nullable=False)
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