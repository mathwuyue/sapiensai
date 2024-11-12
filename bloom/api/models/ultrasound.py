from sqlalchemy import Column, Numeric, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from ..db.base_class import Base

class Ultrasound(Base):
    __tablename__ = "bloom_ultrasounds"

    checkup_id = Column(Integer, ForeignKey("bloom_checkups.id"))
    head_circumference = Column(Numeric(4, 1))
    abdominal_circumference = Column(Numeric(4, 1))
    femur_length = Column(Numeric(4, 1))
    estimated_weight = Column(Numeric(6, 2))
    fetal_position = Column(String(20))
    amniotic_fluid_index = Column(Numeric(4, 1))
    placenta_position = Column(String(20))
    placenta_grade = Column(Integer)

    # Relationships
    checkup = relationship("Checkup", back_populates="ultrasound")