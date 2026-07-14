import json
import re
from utils.ai.exceptions import AIParseError


def parse_json_response(text: str) -> dict:
    """
    Parse AI response and return a Python dictionary.

    Handles:
    - Plain JSON
    - ```json ... ```
    - ``` ... ```
    - Extra text before/after JSON
    """

    if not text:
        raise AIParseError("Empty AI response.")

    text = text.strip()

    # Remove markdown code blocks
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text)
        text = text.replace("```", "").strip()

    # Extract JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise AIParseError("No valid JSON object found in AI response.")

    json_text = text[start:end + 1]

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        raise AIParseError(f"Invalid JSON format: {e}")