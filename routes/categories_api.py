import os, uuid, re
from fastapi import Body
from models.category import Category
from config.database import get_db
from fastapi import (APIRouter,Depends, HTTPException, UploadFile, File, Form, Request)
from sqlalchemy.orm import Session
from repositories.category_repository import CategoryRepository

router = APIRouter(
    prefix="/admin/categories"
)

# Categoty Section Start
@router.post("/category/create")
async def create_category(
    request: Request,
    name: str = Form(...),
    slug: str = Form(None),
    status: int = Form(1),
    commission_type: str = Form("percentage"),
    commission_value: float = Form(0.00),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    admin = getattr(request.state, "admin", None)
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Auto slug
    if not slug:
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

    # Duplicate check
    existing = CategoryRepository().get_by_slug(db, slug)
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    # Image upload
    image_path = None

    if image and image.filename:

        allowed_types = ["image/jpeg", "image/png", "image/webp"]

        if image.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid image type")

        contents = await image.read()

        if len(contents) > 500 * 1024:
            raise HTTPException(status_code=400, detail="Image size too large")

        folder = "static/uploads/categories/"
        os.makedirs(folder, exist_ok=True)

        filename = f"{uuid.uuid4()}.jpg"
        file_location = f"{folder}{filename}"

        with open(file_location, "wb") as f:
            f.write(contents)

        image_path = f"/static/uploads/categories/{filename}"

    # 🔥 Insert
    category = CategoryRepository().create(db, {
        "name": name,
        "slug": slug,
        "status": status,
        "commission_type":commission_type,
        "commission_value":commission_value,
        "image": image_path
    })

    return {
        "status": True,
        "message": "Category created successfully",
        "data": {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "image": category.image,
            "status": category.status
        }
    }

# Category List
@router.get("/category/list")
def category_list(
    request: Request,
    page: int = 1,
    limit: int = 10,
    search: str = None,
    status: str = None,
    db: Session = Depends(get_db)
):

    admin = getattr(request.state, "admin", None)

    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    categories, total = CategoryRepository().get_all(
        db,
        page=page,
        limit=limit,
        search=search,
        status=status
    )

    return {
        "status": True,
        "data": [
            {
                "id": cat.id,
                "name": cat.name,
                "slug": cat.slug,
                "image": cat.image,
                "status": cat.status,
                "commission_type": cat.commission_type,
                "commission_value": cat.commission_value,
                "created_at": cat.created_at.strftime("%Y-%m-%d %H:%M:%S") if cat.created_at else None
            }
            for cat in categories
        ],
        "total": total,
        "page": page,
        "limit": limit
    }

# Category Bulk Deleted
@router.post("/category/bulk-delete")
def bulk_delete_categories(request: Request,payload: dict,db: Session = Depends(get_db),):

    admin = getattr(request.state, "admin", None)

    # 1. AUTH CHECK
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 2. GET IDS
    ids = payload.get("ids", [])

    if not ids or not isinstance(ids, list):
        raise HTTPException(status_code=400, detail="Invalid IDs")

    # 3. VALIDATE IDS (remove invalid values)
    clean_ids = []
    for i in ids:
        try:
            clean_ids.append(int(i))
        except:
            continue

    if not clean_ids:
        raise HTTPException(status_code=400, detail="No valid IDs found")

    # 4. CHECK EXISTING DATA
    categories = db.query(Category)\
        .filter(Category.id.in_(clean_ids),
                Category.deleted_at == None)\
        .all()

    if not categories:
        raise HTTPException(status_code=404, detail="No categories found")

    # 5. SOFT DELETE (SAFE)
    db.query(Category)\
        .filter(Category.id.in_(clean_ids))\
        .update(
            {
                "deleted_at": datetime.utcnow()
            },
            synchronize_session=False
        )

    db.commit()

    return {
        "status": True,
        "message": f"{len(clean_ids)} categories deleted successfully",
        "deleted_ids": clean_ids
    }

# Edit category By id
@router.get("/category/{category_id}")
def get_category(request: Request, category_id: int, db: Session = Depends(get_db)):

    admin = getattr(request.state, "admin", None)

    # 1. AUTH CHECK
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")


    category = CategoryRepository().get_by_id(db, category_id)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return {
        "status": True,
        "data": {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "image": category.image,
            "status": category.status,
            "commission_type": category.commission_type,
            "commission_value": category.commission_value,
            "created_at": category.created_at.strftime("%d %b %Y %I:%M %p")
        }
    }

# Update Category By Id

@router.put("/category/update/{category_id}")
async def update_category(
    request: Request,
    category_id: int,
    name: str = Form(...),
    slug: str = Form(None),
    status: int = Form(...),
    commission_type: str = Form("percentage"),
    commission_value: float = Form(0.00),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):

    admin = getattr(request.state, "admin", None)

    # 1. AUTH CHECK
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")


    category = CategoryRepository().get_by_id(db, category_id)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Auto Slug
    if not slug:
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip("-")

    # Duplicate Slug Check
    duplicate = (
        db.query(Category)
        .filter(
            Category.slug == slug,
            Category.id != category_id,
            Category.deleted_at == None
        )
        .first()
    )

    if duplicate:
        raise HTTPException(status_code=400, detail="Slug already exists")

    image_path = None

    if image and image.filename:

        allowed = ["image/jpeg", "image/png", "image/webp"]

        if image.content_type not in allowed:
            raise HTTPException(status_code=400, detail="Invalid image")

        contents = await image.read()

        if len(contents) > 500 * 1024:
            raise HTTPException(status_code=400, detail="Image too large")

        folder = "static/uploads/categories/"
        os.makedirs(folder, exist_ok=True)

        ext = image.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"

        file_location = os.path.join(folder, filename)

        with open(file_location, "wb") as f:
            f.write(contents)

        image_path = f"/static/uploads/categories/{filename}"

    data = {
        "name": name,
        "slug": slug,
        "status": status,
        "image": image_path,
        "commission_type":commission_type,
        "commission_value":commission_value
    }

    category = CategoryRepository().update(db, category, data)

    return {
        "status": True,
        "message": "Category updated successfully",
        "data": {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "image": category.image,
            "status": category.status,
            "commission_type": category.commission_type,
            "commission_value": category.commission_value
        }
    }

# Category Deleted By Id
@router.delete("/category/delete/{category_id}")
def delete_category(request: Request, category_id: int, db: Session = Depends(get_db)):

    admin = getattr(request.state, "admin", None)

    # 1. AUTH CHECK
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")


    category = db.query(Category).filter(Category.id == category_id, Category.deleted_at == None).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category.deleted_at = datetime.utcnow()

    db.commit()

    return {
        "status": True,
        "message": "Category deleted successfully"
    }
