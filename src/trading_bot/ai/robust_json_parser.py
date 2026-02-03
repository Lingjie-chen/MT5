import json
import re
import logging
from typing import Any, Dict, Optional, List

logger = logging.getLogger(__name__)

def safe_parse_or_default(
    text: str, 
    required_keys: Optional[List[str]] = None, 
    defaults: Optional[Dict[str, Any]] = None, 
    fallback: Optional[Any] = None
) -> Any:
    """
    Robustly parse JSON from LLM output.
    1. Removes Markdown code blocks.
    2. Finds the first outer-most JSON object or array.
    3. Handles common JSON errors (optional).
    4. Validates required keys.
    5. Applies default values.
    """
    if not text:
        return fallback

    # 1. Strip Markdown
    cleaned_text = text.strip()
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[7:]
    if cleaned_text.startswith("```"):
        cleaned_text = cleaned_text[3:]
    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3]
    cleaned_text = cleaned_text.strip()

    parsed_data = None

    # 2. Try direct parsing
    try:
        parsed_data = json.loads(cleaned_text)
    except json.JSONDecodeError:
        # 3. Try to find JSON object using regex
        try:
            # Match { ... }
            match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
            if match:
                parsed_data = json.loads(match.group(0))
            else:
                # Match [ ... ]
                match_arr = re.search(r'\[.*\]', cleaned_text, re.DOTALL)
                if match_arr:
                    parsed_data = json.loads(match_arr.group(0))
        except Exception as e:
            logger.warning(f"JSON regex extraction failed: {e}")

    if parsed_data is None:
        logger.warning(f"Failed to parse JSON from text: {text[:100]}...")
        return fallback

    # 4. Validate & Apply Defaults (Only for Dict)
    if isinstance(parsed_data, dict):
        if defaults:
            for key, value in defaults.items():
                if key not in parsed_data:
                    parsed_data[key] = value
        
        if required_keys:
            missing_keys = [k for k in required_keys if k not in parsed_data]
            if missing_keys:
                logger.warning(f"Parsed JSON missing required keys: {missing_keys}")
                # We can choose to return fallback or keep partial data.
                # Usually better to keep partial data if defaults were applied.
                pass 

    return parsed_data
