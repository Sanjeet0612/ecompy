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
    "tags": [
        "tag1",
        "tag2",
        "tag3",
        "tag4",
        "tag5"
    ]
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
10. Tags MUST be a JSON array containing exactly 5 to 10 SEO relevant tags.
11. Every tag should be short (1-3 words).
12. Tags must be unique.
13. Do not leave tags empty.
14. Do not return tags as a comma separated string.
15. Return at least 5 tags.

IMPORTANT:
All fields are mandatory. Never return empty values for any field including tags.

"""

    return prompt.strip()