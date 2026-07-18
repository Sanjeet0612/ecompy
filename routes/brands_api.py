import os, uuid, re
from fastapi import Body
from models.brand import Brand
from fastapi import (APIRouter, Depends, HTTPException, UploadFile, File, Form, Request)
from sqlalchemy.orm import Session
from repositories.brand_repository import BrandRepository
from config.database import get_db

router = APIRouter(prefix="/admin/brands")


# Brand Section Start
@router.post("/brand/create")
async def create_brand(
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

    # Auto slug
    if not slug:
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

    # Duplicate check
    existing = BrandRepository().get_by_slug(db, slug)
    if existing:
        raise HTTPException(status_code=400, detail="Brand already exists")

    # Image upload
    image_path = None

    if image and image.filename:

        allowed_types = ["image/jpeg", "image/png", "image/webp"]

        if image.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid image type")

        contents = await image.read()

        if len(contents) > 500 * 1024:
            raise HTTPException(status_code=400, detail="Image size too large")

        folder = "static/uploads/brand/"
        os.makedirs(folder, exist_ok=True)

        filename = f"{uuid.uuid4()}.jpg"
        file_location = f"{folder}{filename}"

        with open(file_location, "wb") as f:
            f.write(contents)

        image_path = f"/static/uploads/brand/{filename}"

        result = BrandRepository().create(db, {
            "name": name,
            "slug": slug,
            "status": status,
            "logo": image_path
        })

        if not result["status"]:
            return result

        brand = result["data"]

        return {
            "status": True,
            "message": result["message"],
            "data": {
                "id": brand.id,
                "name": brand.name,
                "slug": brand.slug,
                "logo": brand.logo,
                "status": brand.status
            }
        }

@router.get("/brand/list")
def list_brands(
    page: int = 1,
    limit: int = 10,
    search: str = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    
    result = BrandRepository().get_all(
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
            "name": item.name,
            "slug": item.slug,
            "logo": item.logo,
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

# Edit Brand By id
@router.get("/brand/{brand_id}")
def get_brand(request: Request, brand_id: int, db: Session = Depends(get_db)):

    admin = getattr(request.state, "admin", None)

    # 1. AUTH CHECK
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")


    brand = BrandRepository().get_by_id(db, brand_id)

    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    return {
        "status": True,
        "data": {
            "id": brand.id,
            "name": brand.name,
            "slug": brand.slug,
            "status": brand.status,
            "image": brand.logo,
            "created_at": brand.created_at.strftime("%d %b %Y %I:%M %p")
        }
    }

# Update Brand By id
@router.put("/brand/update/{brand_id}")
async def update_category(
    request: Request,
    brand_id: int,
    name: str = Form(...),
    slug: str = Form(None),
    status: int = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):

    admin = getattr(request.state, "admin", None)

    # 1. AUTH CHECK
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")


    brand = BrandRepository().get_by_id(db, brand_id)

    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    # Auto Slug
    if not slug:
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip("-")

    # Duplicate Slug Check
    duplicate = (
        db.query(Brand)
        .filter(
            Brand.slug == slug,
            Brand.id != brand_id,
            Brand.deleted_at == None
        )
        .first()
    )

    if duplicate:
        raise HTTPException(status_code=400, detail="Slug already exists")

    image_path = None

    if image and image.filename:

        allowed = ["image/jpeg", "image/png", "image/webp"]

        if image.content_type not in allowed:
            raise HTTPException(status_code=400, detail="Invalid Logo")

        contents = await image.read()

        if len(contents) > 500 * 1024:
            raise HTTPException(status_code=400, detail="Logo too large")

        folder = "static/uploads/brand/"
        os.makedirs(folder, exist_ok=True)

        ext = image.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"

        file_location = os.path.join(folder, filename)

        with open(file_location, "wb") as f:
            f.write(contents)

        image_path = f"/static/uploads/brand/{filename}"

    data = {
        "name": name,
        "slug": slug,
        "status": status,
        "image": image_path
    }

    brand = BrandRepository().update(db, brand, data)

    return {
        "status": True,
        "message": "Brand updated successfully",
        "data": {
            "id": brand.id,
            "name": brand.name,
            "slug": brand.slug,
            "image": brand.logo,
            "status": brand.status
           
        }
    }

# Brand Bulk Deleted
@router.post("/brand/bulk-delete")
def bulk_delete_brands(request: Request,payload: dict,db: Session = Depends(get_db),):

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
    brand = db.query(Brand)\
        .filter(Brand.id.in_(clean_ids),
                Brand.deleted_at == None)\
        .all()

    if not brand:
        raise HTTPException(status_code=404, detail="No Brand found")

    # 5. SOFT DELETE (SAFE)
    db.query(Brand)\
        .filter(Brand.id.in_(clean_ids))\
        .update(
            {
                "deleted_at": datetime.utcnow()
            },
            synchronize_session=False
        )

    db.commit()

    return {
        "status": True,
        "message": f"{len(clean_ids)} Brand deleted successfully",
        "deleted_ids": clean_ids
    }

# Brand Single Delete
@router.delete("/brand/delete/{id}")
def delete_brands(
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
        result = BrandRepository().delete(db, id)

        return result

    except Exception as e:
        return {
            "status": False,
            "message": str(e)
        }
