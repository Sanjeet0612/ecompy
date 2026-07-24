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



def validate_blog_response(data: dict) -> dict:
    """
    Validate AI Blog response.
    """

    required_fields = [
        "short_description",
        "description",
        "seo_title",
        "meta_description",
        "meta_keywords",
        "tags",
    ]

    missing = []

    for field in required_fields:
        value = data.get(field)

        if value is None:
            missing.append(field)

    if missing:
        raise ValueError(
            "Missing required fields: " + ", ".join(missing)
        )

    # Clean string values
    data["short_description"] = str(data.get("short_description", "")).strip()
    data["description"] = str(data.get("description", "")).strip()
    data["seo_title"] = str(data.get("seo_title", "")).strip()
    data["meta_description"] = str(data.get("meta_description", "")).strip()
    data["meta_keywords"] = str(data.get("meta_keywords", "")).strip()

    # Validate Tags
    tags = data.get("tags")

    if not tags:
        raise ValueError("Tags are required.")

    if isinstance(tags, list):

        tags = [
            str(tag).strip()
            for tag in tags
            if str(tag).strip()
        ]

        if not tags:
            raise ValueError("Tags are required.")

        data["tags"] = ",".join(tags)

    elif isinstance(tags, str):

        tags = tags.strip()

        if not tags:
            raise ValueError("Tags are required.")

        data["tags"] = tags

    else:
        raise ValueError("Invalid tags format.")

    return data