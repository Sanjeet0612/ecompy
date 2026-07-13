import os, uuid, re, math
from fastapi import Body
from models.category import Category
from models.subcategory import SubCategory
from models.brand import Brand
from models.attribute import Attribute
from models.attribute_value import AttributeValue
from fastapi import (APIRouter, Depends, HTTPException, Response, UploadFile, File, Form, Request)
from sqlalchemy.orm import Session

from config.database import get_db
from repositories.admin_repository import AdminRepository
from repositories.category_repository import CategoryRepository
from schemas.category import CategoryResponse

from repositories.sub_category_repository import SubCategoryRepository

from repositories.brand_repository import BrandRepository
from repositories.attribute_repository import AttributeRepository
from repositories.attribute_repository_value import AttributeValueRepository

from repositories.product_repository import ProductRepository
from schemas.product import ProductCreate

from schemas.admin import AdminLogin
from utils.security import verify_password
from utils.jwt import create_access_token
from utils.gemini import generate_product_content
from utils.file_upload import (upload_image,PRODUCT_MAIN_PATH,PRODUCT_GALLERY_PATH)
from datetime import datetime
from typing import Optional

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

# Attribute Create
@router.post("/attribute/create")
async def create_attribute(
    request: Request,
    name: str = Form(...),
    status: int = Form(1),
    db: Session = Depends(get_db)
):
    admin = getattr(request.state, "admin", None)
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")


    # Duplicate check
    existing = AttributeRepository().get_by_name(db, name)
    if existing:
        raise HTTPException(status_code=400, detail="Attribute already exists")


    attribute = AttributeRepository().create(db, {
            "name": name,
            "status": status
        })

    return {
        "status": True,
        "message": "Attribute created successfully.",
        "data": {
            "id": attribute.id,
            "name": attribute.name,
            "status": attribute.status
        }
    }
# Attribute List
@router.get("/attribute/list")
def list_attribute(
    page: int = 1,
    limit: int = 10,
    search: str = None,
    status: str = None,
    db: Session = Depends(get_db)
):

    attributes, total = AttributeRepository().get_all(
        db=db,
        page=page,
        limit=limit,
        search=search,
        status=status
    )

    data = []

    for item in attributes:
        data.append({
            "id": item.id,
            "name": item.name,
            "status": item.status,
            "updated_at": item.updated_at
        })

    pages = math.ceil(total / limit) if total > 0 else 1

    return {
        "status": True,
        "data": data,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }

# Edit attribute By id
@router.get("/attribute/{attribute_id}")
def get_attribute(request: Request, attribute_id: int, db: Session = Depends(get_db)):

    admin = getattr(request.state, "admin", None)

    # 1. AUTH CHECK
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")


    attribute = AttributeRepository().get_by_id(db, attribute_id)

    if not attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")

    return {
        "status": True,
        "data": {
            "id": attribute.id,
            "name": attribute.name,
            "status": attribute.status,
            "created_at": attribute.created_at.strftime("%d %b %Y %I:%M %p")
        }
    }
# Update attribute By id
@router.put("/attribute/update/{attribute_id}")
async def update_attribute(
    request: Request,
    attribute_id: int,
    name: str = Form(...),
    status: int = Form(...),
    db: Session = Depends(get_db)
):

    admin = getattr(request.state, "admin", None)

    # 1. AUTH CHECK
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")


    attribute = AttributeRepository().get_by_id(db, attribute_id)

    if not attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")

    
    data = {
        "name": name,
        "status": status
    }

    attribute = AttributeRepository().update(db, attribute, data)

    return {
        "status": True,
        "message": "Attribute updated successfully",
        "data": {
            "id": attribute.id,
            "name": attribute.name,
            "status": attribute.status
           
        }
    }

# Attribute Single Delete
@router.delete("/attribute/delete/{id}")
def delete_attribute(
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
        result = AttributeRepository().delete(db, id)

        return result

    except Exception as e:
        return {
            "status": False,
            "message": str(e)
        }

# Attribute Bulk Deleted
@router.post("/attribute/bulk-delete")
def bulk_delete_attribute(request: Request,payload: dict,db: Session = Depends(get_db),):

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
    attribute = db.query(Attribute)\
        .filter(Attribute.id.in_(clean_ids),
                Attribute.deleted_at == None)\
        .all()

    if not attribute:
        raise HTTPException(status_code=404, detail="No Attribute found")

    # 5. SOFT DELETE (SAFE)
    db.query(Attribute)\
        .filter(Attribute.id.in_(clean_ids))\
        .update(
            {
                "deleted_at": datetime.utcnow()
            },
            synchronize_session=False
        )

    db.commit()

    return {
        "status": True,
        "message": f"{len(clean_ids)} Attribute deleted successfully",
        "deleted_ids": clean_ids
    }

#-----------------------Attribute Value Section Start --------------------------------------

# Attribute Value Section Start
@router.post("/attributevalue/create")
async def create_attribute_value(
    request: Request,
    attribute_id: int = Form(...),
    value: str = Form(...),
    status: int = Form(1),
    db: Session = Depends(get_db)
):
    # Check Admin Authentication
    admin = getattr(request.state, "admin", None)
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Validation
    value = value.strip()

    if not value:
        return {
            "status": False,
            "message": "Attribute value is required."
        }

    # Save
    result = AttributeValueRepository().create(db, {
        "attribute_id": attribute_id,
        "value": value,
        "status": status
    })

    if not result["status"]:
        return result

    attributeValues = result["data"]

    return {
        "status": True,
        "message": result["message"],
        "data": [
            {
                "id": attributeValue.id,
                "attribute_id": attributeValue.attribute_id,
                "value": attributeValue.value,
                "status": attributeValue.status
            }
            for attributeValue in attributeValues
        ]
    }

# Attribute List
@router.get("/attributevalue/list")
def list_attribute_value(
    page: int = 1,
    limit: int = 10,
    search: str = None,
    attribute_id: int = None,
    status: str = None,
    db: Session = Depends(get_db)
):

    attribute_values, total = AttributeValueRepository().get_all(
        db=db,
        page=page,
        limit=limit,
        search=search,
        attribute_id=attribute_id,
        status=status
    )

    data = []

    for item in attribute_values:
        data.append({
            "id": item.id,
            "attribute_id": item.attribute_id,
            "attribute_name": item.attribute.name if item.attribute else "",
            "value": item.value,
            "status": item.status,
            "updated_at": item.updated_at.strftime("%d-%m-%Y %I:%M %p") if item.updated_at else ""
        })

    pages = math.ceil(total / limit) if total > 0 else 1

    return {
        "status": True,
        "data": data,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }


# Edit attribute Value By id
@router.get("/attributevalue/{attribute_value_id}")
def get_attribute_value(request: Request, attribute_value_id: int, db: Session = Depends(get_db)):

    admin = getattr(request.state, "admin", None)

    # 1. AUTH CHECK
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")


    attributeValue = AttributeValueRepository().get_by_id(db, attribute_value_id)

    if not attributeValue:
        raise HTTPException(status_code=404, detail="Attribute Value not found")

    return {
        "status": True,
        "data": {
            "id": attributeValue.id,
            "attribute_id": attributeValue.attribute_id,
            "value": attributeValue.value,
            "status": attributeValue.status,
            "created_at": attributeValue.created_at.strftime("%d %b %Y %I:%M %p")
        }
    }

# Update attribute Value By id
@router.put("/attributevalue/update/{id}")
async def update_attribute_value(
    id: int,
    request: Request,
    attribute_id: int = Form(...),
    value: str = Form(...),
    status: int = Form(...),
    db: Session = Depends(get_db)
):
    admin = getattr(request.state, "admin", None)
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Validation
    value = value.strip()

    if not value:
        return {
            "status": False,
            "message": "Attribute value is required."
        }

    # Get Record
    attribute_value = AttributeValueRepository().get_by_id(db, id)

    if not attribute_value:
        return {
            "status": False,
            "message": "Attribute value not found."
        }

    # Update
    result = AttributeValueRepository().update(
        db,
        attribute_value,
        {
            "attribute_id": attribute_id,
            "value": value,
            "status": status
        }
    )

    return result

# Attribute value Single Delete
@router.delete("/attributevalue/delete/{id}")
def delete_attribute_value(
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
        result = AttributeValueRepository().delete(db, id)

        return result

    except Exception as e:
        return {
            "status": False,
            "message": str(e)
        }

# Attribute Value Bulk Deleted
@router.post("/attributevalue/bulk-delete-value")
def bulk_delete_attribute_value(request: Request,payload: dict,db: Session = Depends(get_db),):

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
    attributeValue = db.query(AttributeValue)\
        .filter(AttributeValue.id.in_(clean_ids),
                AttributeValue.deleted_at == None)\
        .all()

    if not attributeValue:
        raise HTTPException(status_code=404, detail="No Attribute Value found")

    # 5. SOFT DELETE (SAFE)
    db.query(AttributeValue)\
        .filter(AttributeValue.id.in_(clean_ids))\
        .update(
            {
                "deleted_at": datetime.utcnow()
            },
            synchronize_session=False
        )

    db.commit()

    return {
        "status": True,
        "message": f"{len(clean_ids)} Attribute deleted successfully",
        "deleted_ids": clean_ids
    }


#-------------------------Product Varient Section Start---------------------------------------

@router.post("/product/get-attribute-values")
async def get_attribute_values(
    request: Request,
    payload: dict = Body(...),
    db: Session = Depends(get_db)
):

    attribute_ids = payload.get("attribute_ids", [])

    values = AttributeValueRepository().get_by_attribute_ids(
        db,
        attribute_ids
    )

    data = []

    for value in values:

        data.append({
            "id": value.id,
            "attribute_id": value.attribute_id,
            "value": value.value
        })

    return {
        "status": True,
        "data": data
    }


#-----------------------Product Save Section start---------------------------

@router.post("/product/create")
async def create_product(
    request: Request,
    category_id: int = Form(...),
    subcategory_id: int = Form(...),
    brand_id: int = Form(...),
    productName: str = Form(...),
    short_description: str = Form(None),
    description: str = Form(None),
    has_variant: int = Form(...),
    sku: str = Form(None),
    price: float = Form(0),
    stock: int = Form(0),
    commission_type: str = Form("percentage"),
    commission_value: float = Form(0),
    status: int = Form(1),
    variant_value_ids: Optional[list[str]] = Form(None, alias="variant_value_ids[]"),
    variant_names: Optional[list[str]] = Form(None, alias="variant_names[]"),
    variant_sku: Optional[list[str]] = Form(None, alias="variant_sku[]"),
    variant_price: Optional[list[float]] = Form(None, alias="variant_price[]"),
    variant_stock: Optional[list[int]] = Form(None, alias="variant_stock[]"),
    variant_status: Optional[list[int]] = Form(None, alias="variant_status[]"),
    main_image: UploadFile = File(None),
    gallery_images: list[UploadFile] = File(alias="gallery_images[]"),
    db: Session = Depends(get_db)
):

    admin = getattr(request.state, "admin", None)

    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Main Image Section 
    main_image_name = None

    if main_image:
        main_image_name = await upload_image(
            main_image,
            PRODUCT_MAIN_PATH
        )
    # Gallery Section
    gallery_image_names = []
    
    for image in gallery_images:
        if image.filename:
            filename = await upload_image(
                image,
                PRODUCT_GALLERY_PATH
            )
            gallery_image_names.append(filename)

    
    try:

        product_data = ProductCreate(
            vendor_id=0,
            category_id=category_id,
            subcategory_id=subcategory_id,
            brand_id=brand_id,

            name=productName,
            slug = productName.strip().lower().replace(" ", "-"),

            sku=sku,
            price=price,
            stock=stock,

            commission_type=commission_type,
            commission_value=commission_value,

            short_description=short_description,
            description=description,

            main_image=main_image_name,

            has_variant=has_variant,
            status=status
        )

        product_repository = ProductRepository(db)
        product = product_repository.create(product_data)
        product_repository.save_gallery_images(product.id,gallery_image_names)

        # Variant Section

        variants = []

        if has_variant == 1:

            for i in range(len(variant_sku)):

                variants.append({
                    "attribute_value_ids": [
                        int(x)
                        for x in variant_value_ids[i].split(",")
                    ],
                    "sku": variant_sku[i],
                    "price": variant_price[i],
                    "stock": variant_stock[i],
                    "status": variant_status[i]
                })

            variant_data = product_repository.save_variants(product.id,variants)

            product_repository.save_variant_values(variant_data)
            

        db.commit()

        return {
            "status": True,
            "message": "Product created successfully.",
            "data": {
                "id": product.id
            }
        }

    except Exception as e:

        db.rollback()

        return {
            "status": False,
            "message": str(e)
        }






@router.post("/admin/product/generate-ai")







# -------------------------Logout Section Start---------------------------------------
@router.post("/api/logout")
def logout(response: Response):
    response.delete_cookie("admin_token")
    return {
        "status": True,
        "message": "Logout successful"
    }