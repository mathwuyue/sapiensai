'''
Core module for the Emma Nutrition application.
'''

import traceback
import orjson
from llm import llm
from prompt import get_food_nutrients_prompt
from nutrition.model import NutritionMacro, NutritionMicro, NutritionMineral, EmmaComment, DietaryData, DietarySummary
from logger import file_error_logger
from utils import extract_json_from_text


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
        file_error_logger.error(f"Error analyzing food image: {error_traceback}")
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


def 
             