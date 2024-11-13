from fastapi import APIRouter
from api.routes.v1 import users, patients, checkups, medical_records

api_router = APIRouter()

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