from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from ..db.base_class import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Patient(Base):
    __tablename__ = "bloom_patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("bloom_users.id"), nullable=False)
    name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    blood_type = Column(String(10))
    rh_factor = Column(String(1))
    phone = Column(String(20))
    emergency_contact = Column(String(50))

    # Relationships
    user = relationship("User", backref="patient")
    checkups = relationship("Checkup", back_populates="patient")