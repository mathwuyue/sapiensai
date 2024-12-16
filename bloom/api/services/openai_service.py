import json
import re
from typing import Dict, Any
from openai import AsyncOpenAI
from api.core.config import settings
from api.schemas.food import (
    FoodAnalyzeBase,
    FoodItem,
    Nutrients,
    MacroNutrients,
    MicroNutrients,
    Minerals,
)

client = AsyncOpenAI(
    api_key=settings.QWEN_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """Extract JSON from text response"""
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if not json_match:
        raise ValueError("No JSON found in response")
    
    try:
        return json.loads(json_match.group(0))
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {str(e)}")

async def analyze_food_image(base64_image: str) -> FoodAnalyzeBase:
    """Analyze food image using Qwen VL API"""
    try:
        response = await client.chat.completions.create(
            model="qwen-vl-max",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Please analyze this food image and provide information in the following JSON format:
                            {
                                "foods": [
                                    {
                                        "food": "name of the food",
                                        "count": "portion count (number)"
                                    }
                                ],
                                "nutrients": {
                                    "macro": {
                                        "calories": "total calories (number)",
                                        "protein": "protein in grams (number)",
                                        "fat": "fat in grams (number)",
                                        "carb": "carbohydrates in grams (number)"
                                    },
                                    "micro": {
                                        "fa": "dietary fiber in grams (number)",
                                        "vc": "vitamin C in mg (number)",
                                        "vd": "vitamin D in mcg (number)"
                                    },
                                    "mineral": {
                                        "calcium": "calcium in mg (number)",
                                        "iron": "iron in mg (number)",
                                        "zinc": "zinc in mg (number)",
                                        "iodine": "iodine in mcg (number)"
                                    }
                                },
                                "summary": "overall nutritional assessment",
                                "advice": "suggestions for improvement"
                            }
                            
                            Please ensure all numerical values are numbers, not strings. 
                            If you cannot determine exact nutritional content, provide reasonable estimates.
                            Keep the summary and advice concise but informative."""
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
            max_tokens=2000,
            temperature=0.2
        )

        content = response.choices[0].message.content
        data = extract_json_from_text(content)
        
        # Convert raw data to Pydantic models
        macro = MacroNutrients(
            calories=float(data["nutrients"]["macro"]["calories"]),
            protein=float(data["nutrients"]["macro"]["protein"]),
            fat=float(data["nutrients"]["macro"]["fat"]),
            carb=float(data["nutrients"]["macro"]["carb"])
        )
        
        micro = MicroNutrients(
            fa=float(data["nutrients"]["micro"]["fa"]),
            vc=float(data["nutrients"]["micro"]["vc"]),
            vd=float(data["nutrients"]["micro"]["vd"])
        )
        
        mineral = Minerals(
            calcium=float(data["nutrients"]["mineral"]["calcium"]),
            iron=float(data["nutrients"]["mineral"]["iron"]),
            zinc=float(data["nutrients"]["mineral"]["zinc"]),
            iodine=float(data["nutrients"]["mineral"]["iodine"])
        )
        
        nutrients = Nutrients(
            macro=macro,
            micro=micro,
            mineral=mineral
        )
        
        # Create final analysis result
        return FoodAnalyzeBase(
            foods=[FoodItem(**item) for item in data["foods"]],
            nutrients=nutrients,
            summary=data["summary"],
            advice=data["advice"]
        )

    except Exception as e:
        raise Exception(f"API error: {str(e)}") 