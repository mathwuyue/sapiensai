from fastapi import APIRouter
from api.routes.v1 import auth, users, patients, checkups, medical_records, food, glucose, profile
from .exercise import router as exercise_router

api_router = APIRouter()

# Auth
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"]
)

# User management
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

# Patient management
api_router.include_router(
    patients.router,
    prefix="/patients",
    tags=["patients"]
)

# Glucose management
api_router.include_router(
    glucose.router,
    prefix="/glucose",
    tags=["glucose"]
)

# Checkup management
api_router.include_router(
    checkups.router,
    prefix="/checkups",
    tags=["checkups"]
)

# Medical records (vital signs, ultrasound, lab results, etc.)
api_router.include_router(
    medical_records.router,
    prefix="/medical-records",
    tags=["medical-records"]
)

# Food management
api_router.include_router(
    food.router,
    prefix="/food",
    tags=["food"]
) 

# Profile management
api_router.include_router(
    profile.router,
    prefix="/profile",
    tags=["profile"]
)
# api_router.include_router(exercise_router, tags=["exercise"])
api_router.include_router(
    exercise_router,
    prefix="/exercise", 
    tags=["exercise"]
)