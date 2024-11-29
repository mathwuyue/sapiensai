from sqlalchemy import Column, String, ForeignKey, Text, Date, BigInteger
from sqlalchemy.orm import relationship
from api.db.base_class import Base, id_generator

class Recommendation(Base):
    __tablename__ = "bloom_recommendations"

    id = Column(BigInteger, primary_key=True, index=True, default=id_generator.generate_id)
    checkup_id = Column(BigInteger, ForeignKey("bloom_checkups.id"), nullable=False)
    category = Column(String(50))
    content = Column(Text, nullable=False)
    priority = Column(String(20))
    valid_until = Column(Date)
    notes = Column(Text)

    # Relationships
    checkup = relationship("Checkup", back_populates="recommendations")