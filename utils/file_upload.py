import os
import uuid
from fastapi import UploadFile

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 500 * 1024  # 500kb

PRODUCT_MAIN_PATH    = "static/uploads/products/main"
PRODUCT_GALLERY_PATH = "static/uploads/products/gallery"
CATEGORY_PATH        = "static/uploads/categories"
SUB_CATEGORY_PATH    = "static/uploads/subcategory"
BRAND_PATH           = "static/uploads/brand"
VENDOR_PATH          = "static/uploads/vendors"


async def upload_image(file: UploadFile, upload_path: str):
    if not file:
        return None

    # Check extension
    if "." not in file.filename:
        raise ValueError("Invalid image file.")

    extension = file.filename.rsplit(".", 1)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Only jpg, jpeg, png and webp images are allowed.")

    # Check file size
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise ValueError("Maximum image size is 500kb.")

    # Reset pointer
    #await file.seek(0)

    # Create folder if not exists
    os.makedirs(upload_path, exist_ok=True)

    # Generate unique filename
    filename = f"{uuid.uuid4().hex}.{extension}"

    filepath = os.path.join(upload_path, filename)

    with open(filepath, "wb") as buffer:
        buffer.write(content)

    return os.path.join(
        upload_path.replace("static/", ""),
        filename
    ).replace("\\", "/")


def delete_image(filename: str):
    if not filename:
        return

    file_path = os.path.join("static", filename.replace("/", os.sep))

    if os.path.exists(file_path):
        os.remove(file_path)