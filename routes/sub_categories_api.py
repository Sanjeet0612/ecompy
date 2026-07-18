import os, uuid, re, math, json
from fastapi import Body
from models.subcategory import SubCategory
from fastapi import (APIRouter, Depends, HTTPException, Response, UploadFile, File, Form, Request)
from sqlalchemy.orm import Session
from config.database import get_db
from repositories.sub_category_repository import SubCategoryRepository

router = APIRouter(
    prefix="/admin/subcategories"
)

# Sub Categoty Section Start
@router.post("/subcategory/create")
def create_subcategory(
    request: Request,
    category_id: int = Form(...),
    name: str = Form(...),
    slug: str = Form(None),
    status: int = Form(1),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):

    try:

        admin = getattr(request.state, "admin", None)
        if not admin:
            raise HTTPException(status_code=403, detail="Not authorized")


        repo = SubCategoryRepository()

        # ---------------- SLUG AUTO ----------------
        if not slug:
            slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

        # ---------------- DUPLICATE CHECK (optional but recommended) ----------------
        existing = db.query(SubCategory).filter(SubCategory.slug == slug).first()
        if existing:
            return {"status": False, "message": "SubCategory already exists"}

        # ---------------- IMAGE UPLOAD ----------------
        image_path = None

        if image is not None and image.filename != "":
            allowed_types = ["image/jpeg", "image/png", "image/webp"]

            if image.content_type not in allowed_types:
                return {"status": False, "message": "Invalid image type"}

            contents = image.file.read()

            if len(contents) > 500 * 1024:
                return {"status": False, "message": "Image size too large"}

            upload_dir = "static/uploads/subcategory/"
            os.makedirs(upload_dir, exist_ok=True)

            file_ext = image.filename.split(".")[-1]
            file_name = f"{uuid.uuid4()}.{file_ext}"

            file_path = os.path.join(upload_dir, file_name)

            with open(file_path, "wb") as f:
                f.write(contents)

            image_path = f"/static/uploads/subcategory/{file_name}"

        # ---------------- DATA PREP ----------------
        data = {
            "category_id": category_id,
            "name": name,
            "slug": slug,
            "status": status,
            "image": image_path
        }

        # ---------------- SAVE ----------------
        result = repo.create(db, data)

        return {
            "status": True,
            "message": "SubCategory created successfully",
            "data": result
        }

    except Exception as e:
        return {
            "status": False,
            "message": str(e)
        }

@router.get("/subcategory/list")
def list_subcategories(
    page: int = 1,
    limit: int = 10,
    search: str = None,
    status: str = None,
    db: Session = Depends(get_db)
):

    result = SubCategoryRepository().get_all(
        db=db,
        page=page,
        limit=limit,
        search=search,
        status=status
    )

    data = []

    for item in result["data"]:
        data.append({
            "id": item.id,
            "category_name": item.category.name if item.category else "",
            "name": item.name,
            "slug": item.slug,
            "image": item.image,
            "status": item.status,
            "updated_at": item.updated_at
        })

    return {
        "status": True,
        "data": data,
        "total": result["total"],
        "page": result["page"],
        "limit": result["limit"],
        "pages": result["pages"]
    }

@router.get("/subcategory/{id}")
def get_subcategory(
    id: int,
    db: Session = Depends(get_db)
):
    subcategory = SubCategoryRepository().get_by_id(db, id)

    if not subcategory:
        raise HTTPException(status_code=404, detail="Sub Category not found")

    return {
        "status": True,
        "data": {
            "id": subcategory.id,
            "category_id": subcategory.category_id,
            "name": subcategory.name,
            "slug": subcategory.slug,
            "image": subcategory.image,
            "status": subcategory.status
        }
    }

# Selecte all sub category basis on category Id
@router.get("/subcategories/{category_id}")
def get_subcategories(
    category_id: int,
    db: Session = Depends(get_db)
):
    subcategories = (
        db.query(SubCategory)
        .filter(
            SubCategory.category_id == category_id,
            SubCategory.status == 1,
            SubCategory.deleted_at == None
        )
        .order_by(SubCategory.name.asc())
        .all()
    )

    return {
        "status": True,
        "data": [
            {
                "id": sub.id,
                "name": sub.name
            }
            for sub in subcategories
        ]
    }

@router.post("/subcategory/update")
async def update_subcategory(
    request: Request,
    id: int = Form(...),
    category_id: int = Form(...),
    name: str = Form(...),
    slug: str = Form(None),
    status: int = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):

    admin = getattr(request.state, "admin", None)
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    subcategory = SubCategoryRepository().get_by_id(db, id)

    if not subcategory:
        raise HTTPException(status_code=404, detail="Sub Category not found")

    # Auto Slug
    if not slug:
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

    image_path = subcategory.image

    # Image Upload
    if image and image.filename:

        allowed_types = ["image/jpeg", "image/png", "image/webp"]

        if image.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid image type")

        contents = await image.read()

        if len(contents) > 500 * 1024:
            raise HTTPException(status_code=400, detail="Image size too large")

        folder = "static/uploads/subcategory/"
        os.makedirs(folder, exist_ok=True)

        filename = f"{uuid.uuid4()}.jpg"
        file_location = f"{folder}{filename}"

        with open(file_location, "wb") as f:
            f.write(contents)

        # Old Image Delete
        if subcategory.image:
            old_image = subcategory.image.lstrip("/")

            if os.path.exists(old_image):
                os.remove(old_image)

        image_path = f"/static/uploads/subcategory/{filename}"

    updated = SubCategoryRepository().update(db, subcategory, {
        "category_id": category_id,
        "name": name,
        "slug": slug,
        "status": status,
        "image": image_path
    })

    return {
        "status": True,
        "message": "Sub Category updated successfully",
        "data": {
            "id": updated.id
        }
    }

@router.post("/subcategory/bulk-delete")
def bulk_delete_subcategory(
    request: Request,
    ids: list[int] = Form(...),
    db: Session = Depends(get_db)
):

    try:
        # ---------------- AUTH CHECK ----------------
        admin = getattr(request.state, "admin", None)

        if not admin:
            raise HTTPException(status_code=403, detail="Not authorized")

        # ---------------- VALIDATION ----------------
        if not ids or len(ids) == 0:
            return {
                "status": False,
                "message": "No items selected"
            }

        # ---------------- SOFT DELETE ----------------
        updated = db.query(SubCategory).filter(
            SubCategory.id.in_(ids),
            SubCategory.deleted_at == None
        ).update(
            {
                "deleted_at": datetime.utcnow()
            },
            synchronize_session=False
        )

        db.commit()

        return {
            "status": True,
            "message": f"{updated} subcategories deleted successfully"
        }

    except Exception as e:
        db.rollback()
        return {
            "status": False,
            "message": str(e)
        }

@router.delete("/subcategory/delete/{id}")
def delete_subcategory(
    request: Request,
    id: int,
    db: Session = Depends(get_db)
):

    try:
        # ---------------- AUTH CHECK ----------------
        admin = getattr(request.state, "admin", None)

        if not admin:
            raise HTTPException(status_code=403, detail="Not authorized")

        # ---------------- DELETE ----------------
        result = SubCategoryRepository().delete(db, id)

        return result

    except Exception as e:
        return {
            "status": False,
            "message": str(e)
        }
