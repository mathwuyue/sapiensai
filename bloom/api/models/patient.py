from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from ..db.base_class import Base

class Patient(Base):
    __tablename__ = "bloom_patients"

    id = None
    user_id = Column(String(36), ForeignKey("bloom_users.user_id"), primary_key=True)
    name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    blood_type = Column(String(10))
    rh_factor = Column(String(1))
    phone = Column(String(20))
    emergency_contact = Column(String(50))

    # Relationships
    user = relationship("User", backref="patient_profile")
    checkups = relationship("Checkup", back_populates="patient")