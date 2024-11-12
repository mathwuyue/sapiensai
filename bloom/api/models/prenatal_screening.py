from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from ..db.base_class import Base

class PrenatalScreening(Base):
    __tablename__ = "bloom_prenatal_screenings"

    checkup_id = Column(Integer, ForeignKey("bloom_checkups.id"))
    screening_type = Column(String(50))
    screening_date = Column(Date)
    result = Column(Text)
    risk_assessment = Column(String(50))
    notes = Column(Text)

    # Relationships
    checkup = relationship("Checkup", back_populates="prenatal_screenings")