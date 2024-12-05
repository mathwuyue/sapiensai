from sqlalchemy import Column, Numeric, Integer, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from api.db.base_class import Base, id_generator

class VitalSigns(Base):
    __tablename__ = "bloom_vital_signs"

    id = Column(BigInteger, primary_key=True, index=True, default=id_generator.generate_id)
    checkup_id = Column(BigInteger, ForeignKey("bloom_checkups.id"), nullable=False)
    weight = Column(Numeric(5, 2))
    weight_gain = Column(Numeric(4, 2))
    blood_pressure_sys = Column(Integer)
    blood_pressure_dia = Column(Integer)
    temperature = Column(Numeric(3, 1))
    fundal_height = Column(Numeric(4, 1))
    fetal_heart_rate = Column(Integer)

    # Relationships
    checkup = relationship("Checkup", back_populates="vital_signs") 