from models.subcategory import SubCategory
from datetime import datetime
import os

class SubCategoryRepository:

    # ---------------- CREATE ----------------
    def create(self, db, data):
        try:
            # duplicate check
            existing = db.query(SubCategory).filter(
                SubCategory.name == data["name"]
            ).first()

            if existing:
                return {"status": False, "message": "SubCategory already exists"}

            data["created_at"] = datetime.utcnow()

            subcategory = SubCategory(**data)
            db.add(subcategory)
            db.commit()
            db.refresh(subcategory)

            return {
                "status": True,
                "message": "SubCategory created successfully",
                "data": subcategory
            }

        except Exception as e:
            db.rollback()
            return {"status": False, "message": str(e)}


    # ---------------- GET ALL ----------------
    def get_all(self, db, page=1, limit=10, search=None, status=None):

        query = db.query(SubCategory).filter(SubCategory.deleted_at == None)

        # 🔍 SEARCH (case-insensitive better)
        if search:
            query = query.filter(SubCategory.name.ilike(f"%{search}%"))

        # 🔥 STATUS FILTER
        if status is not None and status != "":
            query = query.filter(SubCategory.status == status)

        # TOTAL COUNT (before pagination)
        total = query.count()

        # PAGINATION
        subcategories = query.order_by(SubCategory.id.desc()) \
            .offset((page - 1) * limit) \
            .limit(limit) \
            .all()

        return {
            "status": True,
            "data": subcategories,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }


    # ---------------- GET BY ID ----------------
    def get_by_id(self, db, subcategory_id):
        try:
            return db.query(SubCategory).filter(SubCategory.id == subcategory_id).first()
        except Exception as e:
            return {"status": False, "message": str(e)}


    # ---------------- UPDATE ----------------
    def update(self, db, subcategory, data):
        for key, value in data.items():
            setattr(subcategory, key, value)
        subcategory.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(subcategory)
        return subcategory


    # ---------------- DELETE ----------------
    def delete(self, db, subcategory_id):
        try:
            subcategory = db.query(SubCategory).filter(
                SubCategory.id == subcategory_id,
                SubCategory.deleted_at == None
            ).first()

            if not subcategory:
                return {
                    "status": False,
                    "message": "SubCategory not found"
                }

            subcategory.deleted_at = datetime.utcnow()
            db.commit()

            return {
                "status": True,
                "message": "SubCategory deleted successfully"
            }

        except Exception as e:
            db.rollback()
            return {
                "status": False,
                "message": str(e)
            }
     

    def get_dropdown_by_category(
        self,
        db,
        category_id: int
    ):

        subcategories = (
            db.query(SubCategory)
            .filter(
                SubCategory.category_id == category_id,
                SubCategory.status == 1,
                SubCategory.deleted_at.is_(None)
            )
            .order_by(SubCategory.name.asc())
            .all()
        )

        return [
            {
                "id": subcategory.id,
                "name": subcategory.name
            }
            for subcategory in subcategories
        ]