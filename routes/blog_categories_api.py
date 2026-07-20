import os, uuid, re
from datetime import datetime
from fastapi import Body
from models.blog_category import BlogCategory
from config.database import get_db
from fastapi import (APIRouter,Depends, HTTPException, UploadFile, File, Form, Request)
from sqlalchemy.orm import Session
from repositories.blog_category_repository import BlogCategoryRepository

router = APIRouter(
    prefix="/admin/blogcategories"
)


# Categoty Section Start
@router.post("/blog_category/create")
async def create_category(
    request: Request,
    name: str = Form(...),
    slug: str = Form(None),
    status: int = Form(1),
    db: Session = Depends(get_db)
):
    admin = getattr(request.state, "admin", None)
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Auto slug
    if not slug:
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

    # Duplicate check
    existing = BlogCategoryRepository().get_by_slug(db, slug)
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")


    # 🔥 Insert
    category = BlogCategoryRepository().create(db, {
        "name": name,
        "slug": slug,
        "status": status
    })

    return {
        "status": True,
        "message": "Category created successfully",
        "data": {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "status": category.status
        }
    }

# Category List
@router.get("/blog_category/list")
def blog_category_list(
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

    categories, total = BlogCategoryRepository().get_all(
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
                "status": cat.status,
                "created_at": cat.created_at.strftime("%Y-%m-%d %H:%M:%S") if cat.created_at else None
            }
            for cat in categories
        ],
        "total": total,
        "page": page,
        "limit": limit
    }


# Edit category By id
@router.get("/category/{category_id}")
def get_blog_category(request: Request, category_id: int, db: Session = Depends(get_db)):

    admin = getattr(request.state, "admin", None)

    # 1. AUTH CHECK
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")


    category = BlogCategoryRepository().get_by_id(db, category_id)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return {
        "status": True,
        "data": {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "status": category.status,
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
    db: Session = Depends(get_db)
):

    admin = getattr(request.state, "admin", None)

    # 1. AUTH CHECK
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    category = BlogCategoryRepository().get_by_id(db, category_id)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Auto Slug
    if not slug:
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip("-")

    # Duplicate Slug Check
    duplicate = (
        db.query(BlogCategory)
        .filter(
            BlogCategory.slug == slug,
            BlogCategory.id != category_id,
            BlogCategory.deleted_at == None
        )
        .first()
    )

    if duplicate:
        raise HTTPException(status_code=400, detail="Slug already exists")

    data = {
        "name": name,
        "slug": slug,
        "status": status
    }

    category = BlogCategoryRepository().update(db, category, data)

    return {
        "status": True,
        "message": "Category updated successfully",
        "data": {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "status": category.status
        }
    }


# Category Deleted By Id
@router.delete("/category/delete/{category_id}")
def delete_blog_category(request: Request, category_id: int, db: Session = Depends(get_db)):

    admin = getattr(request.state, "admin", None)

    # 1. AUTH CHECK
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")


    category = db.query(BlogCategory).filter(BlogCategory.id == category_id, BlogCategory.deleted_at == None).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category.deleted_at = datetime.utcnow()

    db.commit()

    return {
        "status": True,
        "message": "Category deleted successfully"
    }


# Category Bulk Deleted
@router.post("/category/bulk-delete")
def bulk_delete_blog_categories(request: Request,payload: dict,db: Session = Depends(get_db),):

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
    categories = db.query(BlogCategory)\
        .filter(BlogCategory.id.in_(clean_ids),
                BlogCategory.deleted_at == None)\
        .all()

    if not categories:
        raise HTTPException(status_code=404, detail="No categories found")

    # 5. SOFT DELETE (SAFE)
    db.query(BlogCategory)\
        .filter(BlogCategory.id.in_(clean_ids))\
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
