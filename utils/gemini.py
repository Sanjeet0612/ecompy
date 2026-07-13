from google import genai
from config.settings import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_product_content(product_name, category, brand, features):

    prompt = f"""
    Generate professional ecommerce content.

    Product Name: {product_name}
    Category: {category}
    Brand: {brand}
    Features: {features}

    Return JSON only.

    {{
    "short_description":"",
    "description":"",
    "seo_title":"",
    "meta_description":"",
    "tags":[]
    }}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text