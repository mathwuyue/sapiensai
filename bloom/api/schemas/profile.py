from pydantic import BaseModel, Field
from typing import Optional, Annotated, List
from datetime import datetime

# shared attributes base model
class ProfileBase(BaseModel):
    age: Annotated[int, Field(ge=0, le=100)] = Field(..., description="age in years")
    pre_weight: Annotated[float, Field(ge=30.0, le=200.0)] = Field(..., description="pre-pregnancy weight in kg")
    cur_weight: Annotated[float, Field(ge=30.0, le=200.0)] = Field(..., description="current weight in kg")
    height: Annotated[float, Field(ge=100.0, le=250.0)] = Field(..., description="height in cm")
    
    glucose: Optional[Annotated[float, Field(ge=0.0, le=30.0)]] = Field(None, description="fasting glucose in mmol/L")
    hba1c: Optional[Annotated[float, Field(ge=0.0, le=15.0)]] = Field(None, description="HbA1c percentage")
    blood_pressure_high: Optional[Annotated[int, Field(ge=60, le=250)]] = Field(None, description="systolic blood pressure")
    blood_pressure_low: Optional[Annotated[int, Field(ge=40, le=150)]] = Field(None, description="diastolic blood pressure")
    
    gestational_age: Annotated[int, Field(ge=1, le=45)] = Field(..., description="gestational age in weeks")
    exercise_level: Annotated[int, Field(ge=1, le=4)] = Field(..., description="exercise frequency level")
    
    prescription: Optional[str] = None
    dietary_advice: Optional[str] = None

# Preset Condition Schemas
class PresetConditionBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True

class PresetConditionCreate(PresetConditionBase):
    pass

class PresetCondition(PresetConditionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# User Condition Schemas
class UserConditionBase(BaseModel):
    preset_condition_id: int
    level: Optional[int] = None

class UserConditionCreate(UserConditionBase):
    pass

class UserCondition(UserConditionBase):
    id: int
    profile_id: int
    preset_condition: PresetCondition

    class Config:
        from_attributes = True

# Preset Complication Schemas
class PresetComplicationBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True

class PresetComplicationCreate(PresetComplicationBase):
    pass

class PresetComplication(PresetComplicationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# User Complication Schemas
class UserComplicationBase(BaseModel):
    preset_complication_id: int

class UserComplicationCreate(UserComplicationBase):
    pass

class UserComplication(UserComplicationBase):
    id: int
    profile_id: int
    preset_complication: PresetComplication

    class Config:
        from_attributes = True

# create request model
class ProfileCreate(ProfileBase):
    conditions: List[UserConditionCreate]
    complications: List[UserComplicationCreate]

# update request model
class ProfileUpdate(BaseModel):
    age: Optional[Annotated[int, Field(ge=0, le=100)]] = None
    pre_weight: Optional[Annotated[float, Field(ge=30.0, le=200.0)]] = None
    cur_weight: Optional[Annotated[float, Field(ge=30.0, le=200.0)]] = None
    height: Optional[Annotated[float, Field(ge=100.0, le=250.0)]] = None
    
    glucose: Optional[Annotated[float, Field(ge=0.0, le=30.0)]] = None
    hba1c: Optional[Annotated[float, Field(ge=0.0, le=15.0)]] = None
    blood_pressure_high: Optional[Annotated[int, Field(ge=60, le=250)]] = None
    blood_pressure_low: Optional[Annotated[int, Field(ge=40, le=150)]] = None
    
    gestational_age: Optional[Annotated[int, Field(ge=1, le=45)]] = None
    exercise_level: Optional[Annotated[int, Field(ge=1, le=4)]] = None
    
    prescription: Optional[str] = None
    dietary_advice: Optional[str] = None
    
    conditions: Optional[List[UserConditionCreate]] = None
    complications: Optional[List[UserComplicationCreate]] = None

# return model from database
class Profile(ProfileBase):
    id: int
    user_id: int
    conditions: List[UserCondition]
    complications: List[UserComplication]

    class Config:
        from_attributes = True

# optional: create a simplified response model
class ProfileBasicInfo(BaseModel):
    id: int
    age: int
    gestational_age: int
    conditions: List[UserCondition]
    complications: List[UserComplication]

    class Config:
        from_attributes = True

# Admin view response model
class ProfileAdminView(BaseModel):
    user_id: int
    age: int
    pre_weight: float
    cur_weight: float
    height: float
    glu: Optional[float] = None
    hba1c: Optional[float]
    bph: Optional[int] = None
    bpl: Optional[int] = None
    ga: int
    condition: str
    cond_level: str
    complications: str
    execise: int
    scripts: Optional[str] = None
    advice: Optional[str] = None

    @classmethod
    def from_profile(cls, profile: Profile) -> 'ProfileAdminView':
        # handle conditions
        conditions = []
        levels = []
        for cond in profile.conditions:
            conditions.append(cond.preset_condition.name)
            levels.append(str(cond.level))
        
        condition_str = "None" if not conditions else ", ".join(conditions)
        level_str = "" if not levels else ", ".join(levels)

        # handle complications
        complication_names = []
        for comp in profile.complications:
            complication_names.append(comp.preset_complication.name)
        complication_str = "None" if not complication_names else ", ".join(complication_names)

        return cls(
            user_id=profile.user_id,
            age=profile.age,
            pre_weight=profile.pre_weight,
            cur_weight=profile.cur_weight,
            height=profile.height,
            glu=profile.glucose,
            hba1c=profile.hba1c,
            bph=profile.blood_pressure_high,
            bpl=profile.blood_pressure_low,
            ga=profile.gestational_age,
            condition=condition_str,
            cond_level=level_str,
            complications=complication_str,
            execise=profile.exercise_level,
            scripts=profile.prescription,
            advice=profile.dietary_advice
        )

    class Config:
        from_attributes = True