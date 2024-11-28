from sqlalchemy import Column, Numeric, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..db.base_class import Base

class VitalSigns(Base):
    __tablename__ = "bloom_vital_signs"

    checkup_id = Column(UUID(as_uuid=True), ForeignKey("bloom_checkups.id"), nullable=False)
    weight = Column(Numeric(5, 2))
    weight_gain = Column(Numeric(4, 2))
    blood_pressure_sys = Column(Integer)
    blood_pressure_dia = Column(Integer)
    temperature = Column(Numeric(3, 1))
    fundal_height = Column(Numeric(4, 1))
    fetal_heart_rate = Column(Integer)

    # Relationships
    checkup = relationship("Checkup", back_populates="vital_signs") 