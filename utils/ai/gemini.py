from google import genai
from google.genai import types
from config.settings import GEMINI_API_KEY,GEMINI_MODEL
from utils.ai.prompts.product import build_product_prompt
from utils.ai.prompts.blog import build_blog_prompt
from utils.ai.parser import parse_json_response
from utils.ai.validator import validate_product_response, validate_blog_response
from utils.ai.retry import should_retry, wait_before_retry
import json


client = genai.Client(api_key=GEMINI_API_KEY)


MAX_RETRIES = 3

"""
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
    
    parsed_data = parse_json_response(data["data"])

    print(json.dumps(parsed_data, indent=4, ensure_ascii=False))

    return validate_product_response(parsed_data)
"""


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

    return generate_ai_content(
        prompt=prompt,
        validator=validate_product_response,
        settings=settings
    )

def generate_blog_content(
    title,
    category,
    settings
):

    prompt = build_blog_prompt(
        title=title,
        category=category
    )

    return generate_ai_content(
        prompt=prompt,
        validator=validate_blog_response,
        settings=settings
    )


# Ye 2 Function Common Hai Sabhi k liye
def generate_ai_content(
    prompt: str,
    validator,
    settings
):
    data = generate_content(
        prompt=prompt,
        settings=settings
    )

    if data.get("status") is False:
        return data

    parsed_data = parse_json_response(
        data["data"]
    )

    return validator(parsed_data)

def generate_content(prompt: str, settings):

    for attempt in range(MAX_RETRIES):

        try:

            print(f"AI Attempt: {attempt + 1}")

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )

            return {
                "status": True,
                "data": response.text
            }

        except Exception as e:

            print("=" * 80)
            print(f"AI Attempt : {attempt + 1}/{MAX_RETRIES}")
            print(f"Model      : {GEMINI_MODEL}")
            print(f"Error      : {e}")
            print("=" * 80)

            if should_retry(e) and attempt < MAX_RETRIES - 1:

                wait_before_retry(attempt + 1)
                continue

            print("=" * 80)
            print("AI Generation Failed After Maximum Retries")
            print("=" * 80)

            return {
                "status": False,
                "message": str(e)
            }