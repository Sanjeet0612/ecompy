from models.brand import Brand
from datetime import datetime
from sqlalchemy import or_
import os

class BrandRepository:

    # ---------------- CREATE ----------------
    def create(self, db, data):
        try:

            # Duplicate Name Check
            existing = db.query(Brand).filter(
                or_(
                    Brand.name == data["name"],
                    Brand.slug == data["slug"]
                ),
                Brand.deleted_at == None
            ).first()

            if existing:
                if existing.name == data["name"]:
                    return {
                        "status": False,
                        "message": "Brand name already exists"
                    }

                if existing.slug == data["slug"]:
                    return {
                        "status": False,
                        "message": "Brand slug already exists"
                    }

            data["created_at"] = datetime.utcnow()

            brand = Brand(**data)

            db.add(brand)
            db.commit()
            db.refresh(brand)

            return {
                "status": True,
                "message": "Brand created successfully",
                "data": brand
            }

        except Exception as e:
            db.rollback()

            return {
                "status": False,
                "message": str(e)
            }
        
    # ---------------- GET ALL ----------------
    def get_all(self, db, page=1, limit=10, search=None, status=None):

        query = db.query(Brand).filter(
            Brand.deleted_at == None
        )

        # 🔍 SEARCH
        if search:
            query = query.filter(
                Brand.name.ilike(f"%{search}%")
            )

        # 🔥 STATUS FILTER
        if status is not None and status != "":
            query = query.filter(
                Brand.status == status
            )

        # TOTAL COUNT
        total = query.count()

        # PAGINATION
        brands = (
            query.order_by(Brand.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return {
        "status": True,
        "data": brands,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }

    # ---------------- GET BY ID ----------------
    def get_by_id(self, db, brand_id):
        try:

            return db.query(Brand).filter(
                Brand.id == brand_id,
                Brand.deleted_at == None
            ).first()

        except Exception as e:

            return {
                "status": False,
                "message": str(e)
            }   

    # ---------------- GET BY Slug ----------------
    def get_by_slug(self, db, slug):
        return db.query(Brand).filter(Brand.slug == slug).first()

    # ---------------- UPDATE ----------------
    def update(self, db, brand, data):
        brand.name = data["name"]
        brand.slug = data["slug"]
        brand.status = data["status"]

       
        if data.get("image"):
            # Old image delete
            if brand.logo:
                old_image = brand.logo.lstrip("/")
                if os.path.exists(old_image):
                    os.remove(old_image)

            brand.logo = data["image"]

        db.commit()
        db.refresh(brand)

        return brand
    
    # ---------------- DELETE ----------------
    def delete(self, db, brand_id):
        try:

            brand = db.query(Brand).filter(
                Brand.id == brand_id,
                Brand.deleted_at == None
            ).first()

            if not brand:
                return {
                    "status": False,
                    "message": "Brand not found"
                }

            brand.deleted_at = datetime.utcnow()

            db.commit()

            return {
                "status": True,
                "message": "Brand deleted successfully"
            }

        except Exception as e:
            db.rollback()

            return {
                "status": False,
                "message": str(e)
            }