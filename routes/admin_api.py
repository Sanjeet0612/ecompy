import os, uuid, re
from models.category import Category
from fastapi import (APIRouter, Depends, HTTPException, Response, UploadFile, File, Form, Request)
from sqlalchemy.orm import Session

from config.database import get_db
from repositories.admin_repository import AdminRepository
from repositories.category_repository import CategoryRepository
from schemas.category import CategoryResponse

from schemas.admin import AdminLogin
from utils.security import verify_password
from utils.jwt import create_access_token
from datetime import datetime

router = APIRouter(prefix="/admin")

# Login section Start
@router.post("/api/login")
def admin_login(
    data: AdminLogin,
    response: Response,
    db: Session = Depends(get_db)
):

    admin = AdminRepository.get_by_email(db, data.email)

    if not admin or not verify_password(data.password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if admin.status == 0:
        raise HTTPException(status_code=403, detail="Your account is inactive")

    token = create_access_token({
        "admin_id": admin.id,
        "email": admin.email,
        "role": admin.role,
        "type": "admin"
    })

    response.set_cookie(
        key="admin_token",
        value=token,
        httponly=True,
        samesite="lax",
        path="/"
    )

    return {
        "status": True,
        "message": "Login successful",
        "token": token,
        "admin": {
            "id": admin.id,
            "name": admin.name,
            "email": admin.email,
            "role": admin.role
        }
    }

# Categoty Section Start
@router.post("/category/create")
async def create_category(
    request: Request,
    name: str = Form(...),
    slug: str = Form(None),
    status: int = Form(1),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    admin = getattr(request.state, "admin", None)
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 🔥 Auto slug
    if not slug:
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

    # 🔥 Duplicate check
    existing = CategoryRepository().get_by_slug(db, slug)
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    # 🔥 Image upload
    image_path = None

    if image:

        allowed_types = ["image/jpeg", "image/png", "image/webp"]

        if image.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid image type")

        contents = await image.read()

        if len(contents) > 2 * 1024 * 1024:
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
def bulk_delete_categories(
    request: Request,
    payload: dict,
    db: Session = Depends(get_db),
    
):
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

# Category Deleted By Id
@router.delete("/category/delete/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.deleted_at == None
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category.deleted_at = datetime.utcnow()

    db.commit()

    return {
        "status": True,
        "message": "Category deleted successfully"
    }

# Logout Section Start
@router.post("/api/logout")
def logout(response: Response):
    response.delete_cookie("admin_token")
    return {
        "status": True,
        "message": "Logout successful"
    }