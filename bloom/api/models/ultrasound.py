from sqlalchemy import Column, Numeric, String, ForeignKey, Integer, BigInteger
from sqlalchemy.orm import relationship
from api.db.base_class import Base, id_generator

class Ultrasound(Base):
    __tablename__ = "bloom_ultrasounds"

    id = Column(BigInteger, primary_key=True, index=True, default=id_generator.generate_id)
    checkup_id = Column(BigInteger, ForeignKey("bloom_checkups.id"), nullable=False)
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