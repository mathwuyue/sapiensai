'''
Core module for the Emma Nutrition application.
'''
import os
import traceback
import httpx
import dotenv
from datetime import datetime
from typing import Dict, Any
from llm import llm
from prompt import get_food_nutrients_prompt, emma_glu_summary
from nutrition.model import NutritionMacro, NutritionMicro, NutritionMineral, EmmaComment, DietaryData, DietarySummary, UserPreferenceData, UserBasicInfo
from nutrition.db import UserPreference, MealData
from fastapi import HTTPException
from utils import extract_json_from_text
from logger import logger


dotenv.load_dotenv()
BLOOM_KEY = os.getenv('BLOOM_KEY')


async def analyze_food(image_base64: str) -> list[NutritionMacro, NutritionMicro, NutritionMineral]:
    url = f"data:image/jpeg;base64,{image_base64}"
    prompt = [
        {
            "type": "text",
            "text": get_food_nutrients_prompt()
        }, {
            "type": "image_url",
            "image_url": {
                "url": url
            }
        }
    ]
    try:
        result = await llm(prompt, model='qwen-vl-max', temperature=0.1)
        nutrition_data = extract_json_from_text(result)['items'][0]
        # print(nutrition_data)
        # print(result)
        # return results as NutritionMacro, NutritionMicro, NutritionMineral
        return (
            NutritionMacro(**nutrition_data['macro']),
            NutritionMicro(**nutrition_data['micro']),
            NutritionMineral(**nutrition_data['mineral'])
        )
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"Error analyzing food image: {error_traceback}")
        logger.error(f"Error analyzing food image: {error_traceback}")
        raise e
        
        
# async def meal_comment(meal: str) -> EmmaComment:
#     prompt = [
#         {
#             "type": "text",
#             "text": f"Comment on the following meal: {meal}"
#         }
#     ]
#     try:
#         return await llm(prompt, model='qwen-vl-max', temperature=0.1)
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Failed to generate meal comment: {str(e)}"
#         )
        

async def dietary_recommendation(basicinfo: dict, glu: list, meals: list, orig_plan: str) -> list[DietarySummary, list[DietaryData]]:
    prompt = [
        {
            "type": "text",
            "text": "Provide dietary recommendations for the user"
        }
    ]
    try:
        return await llm(prompt, model='qwen-vl-max', temperature=0.1)
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Failed to get user preferences: {str(e)}\n{error_traceback}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate dietary recommendation: {str(e)}"
        )
        
        
def cal_calories_gdm(bmi: float, weight: float, is_twins: bool, trimester: int) -> float:
    addon = 400 if is_twins else 200
    if bmi < 18.5:
        calories = 35 * weight + addon
    elif bmi >= 18.5 and bmi < 23.9:
        calories = (35 - 5 / 5.4 * (bmi - 18.5)) * weight + addon
    elif bmi >= 24 and bmi < 27.9:
        calories = (30 - 5 / 3.9 * (bmi - 24)) * weight + addon
    else:
        calories = 25 * weight + addon
    if trimester <= 12:
        if calories < 1600:
            calories = 1600
    elif trimester >= 26:
        if calories < 1800:
            calories = 1800
    return calories


def set_user_preferences(user_id: str, preferences: UserPreferenceData) -> None:
    try:
        # Serialize preferences to dictionary
        preferences_dict = preferences.model_dump()
        # Extract appetite from preferences
        appetite = preferences.appetite
        user_pref, created = UserPreference.get_or_create(userid=user_id, defaults={'preference': preferences_dict, 'appetite': appetite})
        if not created:
            user_pref.preference = preferences_dict
            user_pref.appetite = appetite
            user_pref.save()
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Failed to get user preferences: {str(e)}\n{error_traceback}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate dietary recommendation: {str(e)}"
        )
        
        
def get_user_preferences(user_id: str) -> UserPreferenceData:
    try:
        user_pref = UserPreference.get(UserPreference.id == user_id)
        return UserPreferenceData(**user_pref.preference)
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Failed to get user preferences: {str(e)}\n{error_traceback}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate dietary recommendation: {str(e)}"
        )
        

async def get_user_info(user_id: str) -> str:
    try:
        user_data = await httpx.AsyncClient().get(
            f"http://localhost:8000/api/v1/profile/user/{user_id}", 
            headers={"Authorization": f"Bearer {BLOOM_KEY}"}
        )
        return format_user_basic_info(user_data.json())
    except:
        return "暂无"


def format_user_basic_info(data: Dict[str, Any]) -> str:
    info = UserBasicInfo(**data)
    formatted = []
    base_info = [
        f"Age: {info.age}",
        f"Previous Weight: {info.pre_weight}kg",
        f"Current Weight: {info.cur_weight}kg", 
        f"Height: {info.height}cm",
        f"Multiple Pregnancy: {'Yes' if info.is_twins else 'No'}",
        f"Blood Glucose: {info.glu}",
        f"HbA1c: {info.hba1c}%",
        f"Blood Pressure: {info.bph}/{info.bpl}",
        f"Gestational Age: {info.ga} weeks",
        f"Condition: {info.condition} (Level {info.cond_level})",
        f"Complications: {info.complication}",
        f"Exercise Level: {info.execise}"
    ]
    if info.scripts:
        formatted.append(f"Prescribed scripts: {info.scripts}")
    if info.advice:
        formatted.append(f"Doctor's advice for dietary: {info.advice}")
    
    formatted.extend(base_info)
    return "\n".join(formatted)


def get_meal_data(user_id: str, date: datetime, offset: int) -> list[MealData]:
    meals = MealData.select().where(MealData.userid == user_id)
    return meals


async def get_glu_summary(user_id: str) -> list:
    current_date = datetime.now().strftime("%Y-%m-%d")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8000/api/v1/glucose/user/{user_id}",
                params={"date": current_date, "offset": 7},
                headers={"Authorization": f"Bearer {BLOOM_KEY}"}
            )
            response.raise_for_status()
            glu_records = response.json()
            prompt = emma_glu_summary(glu_records)
            return await llm(prompt)
    except Exception as e:
        logger.error(f"Failed to get glucose data: {str(e)}")
        return []


def get_fitness_data():
    pass