"""
Core module for the Emma Nutrition application.
"""

import os
import traceback
from datetime import datetime, timedelta
from typing import Any, Dict, Tuple

import dotenv
import httpx
import orjson
from fastapi import HTTPException

from health.model import (
    DietaryData,
    DietarySummary,
    EmmaComment,
    NutritionMacro,
    NutritionMicro,
    NutritionMineral,
    UserBasicInfo,
    UserPreferenceData,
)
from llm import llm
from logger import logger
from prompt import (
    emma_exercise_summary,
    emma_glu_summary,
    get_food_nutrients_prompt,
    user_preference_summary,
)
from utils import extract_json_from_text

dotenv.load_dotenv()
BLOOM_KEY = os.getenv("BLOOM_KEY")


async def analyze_food(user_id: str, image_url: str) -> list[dict]:
    """
    Analyze food image to get the food name and portion
    """
    try:
        # query
        query = [
            {
                "type": "text",
                "text": "",
            },
            {"type": "image_url", "image_url": {"url": image_url}},
        ]
        # Analyze food image
        food_info = await llm(query, model="qwen-vl-max", temperature=0.1, is_text=True)
        return food_info
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Failed to analyze food image: {str(e)}\n{error_traceback}")
        raise HTTPException(
            status_code=500, detail=f"Failed to analyze food image: {str(e)}"
        )


async def analyze_food_old(
    user_id, image_base64: str, meal_type: int
) -> list[NutritionMacro, NutritionMicro, NutritionMineral]:
    url = f"data:image/jpeg;base64,{image_base64}"
    # get products
    products = get_products()
    userinfo = await get_user_info(user_id, is_formated=False)
    if type(userinfo) is str:
        userinfo = {"pre_weight": 59.3, "is_twin": False, "height": 1.77, "ga": 12}
    bmi = userinfo["pre_weight"] / (userinfo["height"] ** 2)
    guidelines = {
        "calories": cal_calories_gdm(
            bmi, userinfo["pre_weight"], userinfo["is_twin"], userinfo["ga"]
        ),
        "protein": cal_protein(userinfo["ga"]),
    }
    prompt = [
        {
            "type": "text",
            "text": get_food_nutrients_prompt(
                meal_type=meal_type, products=products, guidelines=guidelines
            ),
        },
        {"type": "image_url", "image_url": {"url": url}},
    ]
    try:
        result = await llm(prompt, model="qwen-vl-max", temperature=0.1, is_text=True)
        nutrition_data = extract_json_from_text(result)["items"][0]
        # print(nutrition_data)
        return nutrition_data
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"Error analyzing food image: {error_traceback}")
        logger.error(f"Error analyzing food image: {error_traceback}")
        raise e


async def dietary_recommendation(
    user_id: str,
) -> list[DietarySummary, list[DietaryData]]:
    """TODO: did not consider previous plan"""
    # userinfo
    userinfo = await get_user_info(user_id, is_formated=True)
    # user_preference
    user_preference = await get_user_preference_summary(user_id)
    # glu summary
    glu_summary = await get_glu_summary(user_id)
    try:
        pass
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Failed to get user preferences: {str(e)}\n{error_traceback}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate dietary recommendation: {str(e)}",
        )


def cal_calories_gdm(bmi: float, weight: float, is_twins: bool, ga: int) -> float:
    addon = 400 if is_twins else 200
    if bmi < 18.5:
        calories = 35 * weight + addon
    elif bmi >= 18.5 and bmi < 23.9:
        calories = (35 - 5 / 5.4 * (bmi - 18.5)) * weight + addon
    elif bmi >= 24 and bmi < 27.9:
        calories = (30 - 5 / 3.9 * (bmi - 24)) * weight + addon
    else:
        calories = 25 * weight + addon
    if ga <= 12:
        if calories < 1600:
            calories = 1600
    elif ga >= 26:
        if calories < 1800:
            calories = 1800
    return calories


def cal_protein(ga: int) -> int:
    if ga <= 12:
        return 46
    return 71


def set_user_preferences(user_id: str, preferences: UserPreferenceData) -> None:
    try:
        # Serialize preferences to dictionary
        preferences_dict = preferences.model_dump()
        # Extract appetite from preferences
        appetite = preferences.appetite
        user_pref, created = UserPreference.get_or_create(
            userid=user_id,
            defaults={"preference": preferences_dict, "appetite": appetite},
        )
        if not created:
            user_pref.preference = preferences_dict
            user_pref.appetite = appetite
            user_pref.save()
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Failed to get user preferences: {str(e)}\n{error_traceback}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate dietary recommendation: {str(e)}",
        )


def get_user_preferences(user_id: str) -> UserPreferenceData:
    try:
        user_pref = UserPreference.select().where(UserPreference.userid == user_id)
        if user_pref:
            return UserPreferenceData(**user_pref.preference)
        return None
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Failed to get user preferences: {str(e)}\n{error_traceback}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate dietary recommendation: {str(e)}",
        )


async def get_user_preference_summary(user_id: str) -> str:
    user_preference = get_user_preferences(user_id)
    if user_preference:
        user_preference_json = user_preference.model_dump_json()
        query = user_preference_summary(user_preference_json)
        resp = await llm(query)
    else:
        resp = "User has no preferences"
    return resp


def get_products() -> str:
    products = Product.select()
    return "\n".join([f"{i+1}. {p.name}: {p.brief}" for i, p in enumerate(products)])


async def get_user_info(user_id: str, is_formated=False) -> str:
    try:
        user_data = await httpx.AsyncClient().get(
            f"http://localhost:8000/api/v1/profile/user/{user_id}",
            headers={"Authorization": f"Bearer {BLOOM_KEY}"},
        )
        if is_formated:
            return format_user_basic_info(user_data.json())
        return user_data.json()
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
        f"Complications: {info.complications}",
        f"Exercise Level: {info.execise}",
    ]
    if info.scripts:
        formatted.append(f"Prescribed scripts: {info.scripts}")
    if info.advice:
        formatted.append(f"Doctor's advice for dietary: {info.advice}")

    formatted.extend(base_info)
    return "\n".join(formatted)


def get_meal_data(user_id: str, date: datetime, offset: int) -> list[MealData]:
    start_date = date - timedelta(days=offset)
    meals = MealData.select(
        MealData.type, MealData.food, MealData.nutrient, MealData.created_at
    ).where(
        (MealData.userid == user_id) & (MealData.created_at.between(start_date, date))
    )
    return meals


def calculate_nutrition_per_day(user_id: str, date: datetime) -> dict:
    """
    Get 7 days meal record to calculate the nutrition from food per day
    """
    # get meal data
    meals = get_meal_data(user_id, date, 7)
    # group them by date
    # Group meals by day
    daily_totals = {}

    for meal in meals:
        # Truncate datetime to day
        day = meal.created_at.date()

        if day not in daily_totals:
            daily_totals[day] = {
                "macro": NutritionMacro(calories=0, protein=0, fat=0, carb=0),
                "micro": NutritionMicro(fa=0, vc=0, vd=0),
                "mineral": NutritionMineral(calcium=0, iron=0, zinc=0, iodine=0),
            }
        # Add nutrients from current meal
        nutrients = meal.nutrient
        macro = nutrients["macro"]
        micro = nutrients["micro"]
        mineral = nutrients["mineral"]
        # Sum macro nutrients
        daily_totals[day]["macro"].calories += macro.get("calories", 0)
        daily_totals[day]["macro"].protein += macro.get("protein", 0)
        daily_totals[day]["macro"].fat += macro.get("fat", 0)
        daily_totals[day]["macro"].carb += macro.get("carb", 0)
        # Sum micro nutrients
        daily_totals[day]["micro"].fa += micro.get("fa", 0)
        daily_totals[day]["micro"].vc += micro.get("vc", 0)
        daily_totals[day]["micro"].vd += micro.get("vd", 0)
        # Sum minerals
        daily_totals[day]["mineral"].calcium += mineral.get("calcium", 0)
        daily_totals[day]["mineral"].iron += mineral.get("iron", 0)
        daily_totals[day]["mineral"].zinc += mineral.get("zinc", 0)
        daily_totals[day]["mineral"].iodine += mineral.get("iodine", 0)
    # Format output string
    output = []
    for day, nutrients in sorted(daily_totals.items()):
        macro = nutrients["macro"]
        micro = nutrients["micro"]
        mineral = nutrients["mineral"]
        # final string
        day_str = f"Day {day.strftime('%m-%d')}: "
        day_str += f"Calories {macro.calories:.1f}g, "
        day_str += f"Protein {macro.protein:.1f}g, "
        day_str += f"Fat {macro.fat:.1f}g, "
        day_str += f"Carb {macro.carb:.1f}g, "
        day_str += f"Folic Acid {micro.fa:.1f}mcg, "
        day_str += f"VitC {micro.vc:.1f}mg, "
        day_str += f"VitD {micro.vd:.1f}mcg, "
        day_str += f"Calcium {mineral.calcium:.1f}mg, "
        day_str += f"Iron {mineral.iron:.1f}mg, "
        day_str += f"Zinc {mineral.zinc:.1f}mg, "
        day_str += f"Iodine {mineral.iodine:.1f}mcg"
        output.append(day_str)
    return "".join(output)


async def get_glu_summary(user_id: str) -> list:
    current_date = datetime.now().strftime("%Y-%m-%d")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8000/api/v1/glucose/user/{user_id}",
                params={"date": current_date, "offset": 7},
                headers={"Authorization": f"Bearer {BLOOM_KEY}"},
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


def format_exercise_records(previous_records) -> dict:
    """Format ExerciseData records into standardized JSON structure"""
    formatted_data = []

    for record in previous_records:
        formatted_data.append(
            {
                "datetime": record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "exercise": record.exercise,
                "intensity": record.intensity,
                "duration": record.duration,
                "calories": float(record.calories),
            }
        )

    return {"total": len(formatted_data), "data": formatted_data}
