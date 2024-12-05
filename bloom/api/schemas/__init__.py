from .user import User, UserCreate, UserUpdate, UserInDB
from .patient import Patient, PatientCreate, PatientUpdate
from .checkup import Checkup, CheckupCreate, CheckupUpdate
from .vital_signs import VitalSigns, VitalSignsCreate, VitalSignsUpdate
from .ultrasound import Ultrasound, UltrasoundCreate, UltrasoundUpdate
from .lab_results import LabResults, LabResultsCreate, LabResultsUpdate
from .prenatal_screening import PrenatalScreening, PrenatalScreeningCreate, PrenatalScreeningUpdate
from .recommendation import Recommendation, RecommendationCreate, RecommendationUpdate
from .food import FoodAnalysis, FoodItem
from .glucose import Glucose, GlucoseCreate, GlucoseUpdate
from .profile import Profile, ProfileCreate, ProfileUpdate, UserCondition, UserComplication
from pydantic import BaseModel

__all__ = [
    "User", "UserCreate", "UserUpdate", "UserInDB",
    "Patient", "PatientCreate", "PatientUpdate",
    "Checkup", "CheckupCreate", "CheckupUpdate",
    "VitalSigns", "VitalSignsCreate", "VitalSignsUpdate",
    "Ultrasound", "UltrasoundCreate", "UltrasoundUpdate",
    "LabResults", "LabResultsCreate", "LabResultsUpdate",
    "PrenatalScreening", "PrenatalScreeningCreate", "PrenatalScreeningUpdate",
    "Recommendation", "RecommendationCreate", "RecommendationUpdate",
    "FoodAnalysis", "FoodItem",
    "Glucose", "GlucoseCreate", "GlucoseUpdate",
    "Profile", "ProfileCreate", "ProfileUpdate",
    "UserCondition", "UserComplication"
]

class TokenPayload(BaseModel):
    sub: str
    exp: int | None = None

    @property
    def user_id(self) -> int:
        return int(self.sub)
