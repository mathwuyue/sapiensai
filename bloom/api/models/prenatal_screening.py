from sqlalchemy import Column, String, ForeignKey, Text, Date, BigInteger
from sqlalchemy.orm import relationship
from api.db.base_class import Base, id_generator

class PrenatalScreening(Base):
    __tablename__ = "bloom_prenatal_screenings"

    id = Column(BigInteger, primary_key=True, index=True, default=id_generator.generate_id)
    checkup_id = Column(BigInteger, ForeignKey("bloom_checkups.id"), nullable=False)
    screening_type = Column(String(50))
    screening_date = Column(Date)
    result = Column(Text)
    risk_assessment = Column(String(50))
    notes = Column(Text)

    # Relationships
    checkup = relationship("Checkup", back_populates="prenatal_screenings")