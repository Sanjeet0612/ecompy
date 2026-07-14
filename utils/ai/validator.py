def validate_product_response(data: dict) -> dict:
    """
    Validate AI product response.
    """

    required_fields = [
        "short_description",
        "description",
        "specifications",
        "seo_title",
        "meta_description",
        "meta_keywords",
        "tags"
    ]

    for field in required_fields:

        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    return data