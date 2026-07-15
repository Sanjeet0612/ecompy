from google import genai
from google.genai import types
from config.settings import GEMINI_API_KEY
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
        features,
        settings
):

    prompt = build_product_prompt(
        product_name=product_name,
        category=category,
        sub_category=sub_category,
        brand=brand,
        features=features,
        settings=settings
    )

    data = generate_content(
        prompt=prompt,
        settings=settings
    )

    if data.get("status") is False:
        return data

    return validate_product_response(data)
    


def generate_content(prompt: str, settings):

    model = settings.model if settings else "gemini-3.5-flash"
    temperature = float(settings.temperature) if settings else 0.7
    top_p = float(settings.top_p) if settings else 0.95
    max_output_tokens = int(settings.max_output_tokens) if settings else 8192

    try:
        last_error = None

        for _ in range(MAX_RETRIES):

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        top_p=top_p,
                        max_output_tokens=max_output_tokens
                    )
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