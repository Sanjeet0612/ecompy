"""
Product AI Prompt Builder
"""


def build_product_prompt(
    product_name: str,
    category: str = "",
    sub_category: str = "",
    brand: str = "",
    features: str = ""
) -> str:

    return f"""
You are an expert eCommerce content writer and SEO specialist.

Create premium-quality product content for an online eCommerce website.

==================================================
PRODUCT INFORMATION
==================================================

Product Name:
{product_name}

Category:
{category or "Not Provided"}

Brand:
{brand or "Not Provided"}

Sub Category:
{sub_category or "Not Provided"}

Features:
{features or "Not Provided"}

==================================================
RULES
==================================================

- Write professional, human-like content.
- Never mention AI.
- Never generate fake specifications.
- Use only the provided product information.
- Return ONLY valid JSON.
- Do not wrap JSON inside markdown.
- The description must contain valid HTML.
- The description should be SEO friendly.

==================================================
RETURN JSON
==================================================

{{
    "short_description": "",
    "description": "",
    "specifications": [],
    "seo_title": "",
    "meta_description": "",
    "meta_keywords": "",
    "tags": []
}}
"""