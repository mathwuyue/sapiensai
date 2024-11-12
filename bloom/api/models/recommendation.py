from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from ..db.base_class import Base

class Recommendation(Base):
    __tablename__ = "bloom_recommendations"

    checkup_id = Column(Integer, ForeignKey("bloom_checkups.id"))
    category = Column(String(50))
    content = Column(Text, nullable=False)
    priority = Column(String(20))
    valid_until = Column(Date)
    notes = Column(Text)

    # Relationships
    checkup = relationship("Checkup", back_populates="recommendations")