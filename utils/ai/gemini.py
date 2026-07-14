import time
from google import genai

from config.settings import GEMINI_API_KEY, GEMINI_MODEL

from utils.ai.prompts.product import build_product_prompt
from utils.ai.parser import parse_json_response
from utils.ai.validator import validate_product_response
from utils.ai.retry import should_retry, wait_before_retry
#from utils.ai.exceptions import (AIQuotaExceededError,AIConnectionError,AIRetryLimitExceededError)

client = genai.Client(api_key=GEMINI_API_KEY)
MAX_RETRIES = 3

def generate_product_content(
        product_name,
        category,
        sub_category,
        brand,
        features
):

    prompt = build_product_prompt(
        product_name=product_name,
        category=category,
        sub_category=sub_category,
        brand=brand,
        features=features
    )

    data = generate_content(prompt)

    if data.get("status") is False:
        return data

    return validate_product_response(data)
    


def generate_content(prompt: str):
    
    try:
        last_error = None

        for _ in range(MAX_RETRIES):
            try:
                response = client.models.generate_content(
                    model=GEMINI_MODEL,contents=prompt
                )

                data = parse_json_response(response.text)
                return data

            except Exception as e:
                last_error = e

                if should_retry(e):
                    wait_before_retry()
                    continue

                raise

        raise last_error

    except Exception as e:

        return {
            "status": False,
            "message": str(e),
             "data": None
        }    