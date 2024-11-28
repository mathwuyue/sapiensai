import json
import re
from typing import Dict, Any
from openai import AsyncOpenAI
from api.core.config import settings
from api.schemas.food import FoodAnalysis, FoodItem

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Extract JSON from text response, handling cases where JSON might be within markdown code blocks
    or mixed with other text
    """
    # Try to find JSON block in markdown
    json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Try to find any JSON-like structure
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            raise ValueError("No JSON found in response")
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {str(e)}")

async def analyze_food_image(base64_image: str) -> FoodAnalysis:
    """
    Analyze food image using OpenAI's Vision API
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Please analyze this food image and provide the following information in JSON format:
                                    {
                                        "items": [
                                            {
                                                "name": "food name",
                                                "calories": estimated calories (number),
                                                "portion": "portion size",
                                                "protein": estimated protein in grams (number),
                                                "carbs": estimated carbs in grams (number),
                                                "fat": estimated fat in grams (number)
                                            }
                                        ],
                                        "image_description": "brief description of the image"
                                    }"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )

        # Extract and parse JSON from response
        content = response.choices[0].message.content
        data = extract_json_from_text(content)
        
        # Convert parsed data to FoodItems
        food_items = [
            FoodItem(
                name=item["name"],
                calories=float(item["calories"]),
                portion=item.get("portion"),
                protein=float(item["protein"]) if "protein" in item else None,
                carbs=float(item["carbs"]) if "carbs" in item else None,
                fat=float(item["fat"]) if "fat" in item else None
            )
            for item in data["items"]
        ]
        
        # Create and return FoodAnalysis
        return FoodAnalysis(
            items=food_items,
            total_calories=sum(item.calories for item in food_items),
            image_description=data["image_description"]
        )

    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}") 