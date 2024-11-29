# Description: Utility functions for the project
from typing import Any, Dict
import re
import orjson as json


def make_table_name(model_class):
    model_name = model_class.__name__
    return 'emma_' + model_name.lower()
    
    
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