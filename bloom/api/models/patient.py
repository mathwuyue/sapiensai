from sqlalchemy import Column, String, Date, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from api.db.base_class import Base, id_generator

class Patient(Base):
    __tablename__ = "bloom_patients"

    id = Column(BigInteger, primary_key=True, index=True, default=id_generator.generate_id)
    user_id = Column(BigInteger, ForeignKey("bloom_users.id"), nullable=False)
    name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    blood_type = Column(String(10))
    rh_factor = Column(String(1))
    phone = Column(String(20))
    emergency_contact = Column(String(50))

    # Relationships
    user = relationship("User", backref="patient")