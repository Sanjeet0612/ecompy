import json


def build_blog_prompt(
    title: str,
    category: str = ""
):
    prompt = f"""
You are an expert SEO content writer.

Generate a professional blog in valid JSON format only.

Blog Title:
{title}

Category:
{category}

Return ONLY valid JSON.

Structure:

{{
    "short_description": "",
    "description": "",
    "seo_title": "",
    "meta_description": "",
    "meta_keywords": "",
    "tags": []
}}

Rules:

1. Output ONLY JSON.
2. Do not wrap JSON inside markdown.
3. Description must be HTML.
4. Use:
   - <h2>
   - <h3>
   - <p>
   - <ul>
   - <li>
5. Description should be around 800-1200 words.
6. Write SEO optimized content.
7. SEO Title should be under 60 characters.
8. Meta Description should be under 160 characters.
9. Meta Keywords should be comma separated string.
10. Tags should be JSON array.
11. Generate natural and human readable content.
12. Do not include any explanation outside JSON.
"""

    return prompt.strip()