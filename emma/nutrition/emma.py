'''
Core module for the Emma Nutrition application.
'''
import os
import traceback
import httpx
import dotenv
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
from llm import llm
from prompt import get_food_nutrients_prompt, emma_glu_summary, emma_exercise_summary
from nutrition.model import NutritionMacro, NutritionMicro, NutritionMineral, EmmaComment, DietaryData, DietarySummary, UserPreferenceData, UserBasicInfo
from nutrition.db import db, UserPreference, MealData, ExerciseData, ExerciseDatabase
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
    start_date = date - timedelta(days=offset)
    meals = MealData.select(MealData.type, MealData.food, MealData.nutrient, MealData.created_at).where(
        (MealData.userid == user_id) &
        (MealData.created_at.between(start_date, date))
    )
    return meals


def calculate_nutrition_per_day(user_id: str, date: datetime) -> dict:
    '''
    Get 7 days meal record to calculate the nutrition from food per day
    '''
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
                'macro': NutritionMacro(calories=0, protein=0, fat=0, carb=0),
                'micro': NutritionMicro(fa=0, vc=0, vd=0),
                'mineral': NutritionMineral(calcium=0, iron=0, zinc=0, iodine=0)
            }
        # Add nutrients from current meal
        nutrients = meal.nutrient
        macro = nutrients['macro']
        micro = nutrients['micro']
        mineral = nutrients['mineral']
        # Sum macro nutrients
        daily_totals[day]['macro'].calories += macro.get('calories', 0)
        daily_totals[day]['macro'].protein += macro.get('protein', 0)
        daily_totals[day]['macro'].fat += macro.get('fat', 0)
        daily_totals[day]['macro'].carb += macro.get('carb', 0)
        # Sum micro nutrients
        daily_totals[day]['micro'].fa += micro.get('fa', 0)
        daily_totals[day]['micro'].vc += micro.get('vc', 0)
        daily_totals[day]['micro'].vd += micro.get('vd', 0)
        # Sum minerals
        daily_totals[day]['mineral'].calcium += mineral.get('calcium', 0)
        daily_totals[day]['mineral'].iron += mineral.get('iron', 0)
        daily_totals[day]['mineral'].zinc += mineral.get('zinc', 0)
        daily_totals[day]['mineral'].iodine += mineral.get('iodine', 0)
    # Format output string
    output = []
    for day, nutrients in sorted(daily_totals.items()):
        macro = nutrients['macro']
        micro = nutrients['micro']
        mineral = nutrients['mineral']
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


def cal_calories_met(weight: float, duration: float, met: float) -> float:
    met * duration / 60 * 1.05 * weight
    
    
def cal_max_bpm(age: int) -> float:
    if not age:
        age = 30
    return 208 - 0.7 * age


def cal_exercise_bpm_range(age: int) -> Tuple[int, int]:
    return (int(0.6 * (220 - age)), int(0.89 * (220 - age)))


async def get_exercise_summary(user_id: str, exercise: str, intensity: str, duration: float, bpm: float, start_time, remark: str) -> Tuple[EmmaComment, float]:
    '''
    TODO: How to get the meal time?
    '''
    # get from db
    with db.atomic():
        exercise_data = ExerciseDatabase.get_or_none((ExerciseDatabase.exercise == exercise) & (ExerciseDatabase.type == intensity))
        # Get exercise records
        previous_records = ExerciseData.select().where(
            (ExerciseData.user_id == user_id) & 
            (ExerciseData.created_at.between(datetime.now() - timedelta(days=7), datetime.now()))
        ).order_by(ExerciseData.created_at.desc())
    # calcualte caories. Check ExerciseDatabase for the formula
    if not exercise_data:
        met = 0.0  # Default value
    else:
        met = exercise_data.calories
    # get user info
    user_data_response = await httpx.AsyncClient().get(
        f"http://localhost:8000/api/v1/profile/user/{user_id}", 
        headers={"Authorization": f"Bearer {BLOOM_KEY}"}
    )
    user_data_response.raise_for_status()
    # user_data = user_data_response.json()
    user_data = UserBasicInfo(**user_data_response.json())
    # print(user_data)
    # Calculate calories based on duration and base calories from database
    calories = cal_calories_met(float(user_data.cur_weight), float(duration), float(met))
    conditions = f"{user_data.condition} (Level {user_data.cond_level})"
    new_record = {"exercise": exercise, "intensity": intensity, "duration": duration, "calories": calories, "bpm": bpm, "start_time": start_time, "remark": remark}
    # format records
    exercise_records = format_exercise_records(previous_records)
    # calculate exercise bpm range
    min_bpm, max_bpm = cal_exercise_bpm_range(user_data.age)
    # prompt
    prompt = emma_exercise_summary(new_record, exercise_records, user_data.cur_weight, user_data.ga, conditions, user_data.complications, {'min': min_bpm, 'max': max_bpm})
    print(prompt)
    llm_json = extract_json_from_text(await llm(prompt))
    if not calories:
        calories = llm_json['calories']
    return EmmaComment(**llm_json), calories


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


def format_exercise_records(previous_records) -> dict:
    """Format ExerciseData records into standardized JSON structure"""
    formatted_data = []
    
    for record in previous_records:
        formatted_data.append({
            "datetime": record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "exercise": record.exercise,
            "intensity": record.intensity,
            "duration": record.duration,
            "calories": float(record.calories)
        })
    
    return {
        "total": len(formatted_data),
        "data": formatted_data
    }