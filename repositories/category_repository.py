from models.category import Category
from datetime import datetime
import os

class CategoryRepository:

    def create(self, db, data):
        category = Category(**data)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    def get_all(self, db, page=1, limit=10, search=None, status=None):
        query = db.query(Category).filter(Category.deleted_at == None)

        # 🔍 SEARCH
        if search:
            query = query.filter(Category.name.like(f"%{search}%"))

        # 🔥 STATUS FILTER
        if status is not None and status != "":
            query = query.filter(Category.status == status)

        # TOTAL COUNT (IMPORTANT)
        total = query.count()

        # PAGINATION
        categories = query.order_by(Category.id.desc()) \
            .offset((page - 1) * limit) \
            .limit(limit) \
            .all()

        return categories, total

    def get_by_id(self, db, category_id):
        return db.query(Category).filter(Category.id == category_id, Category.deleted_at == None).first()

    def get_by_slug(self, db, slug):
        return db.query(Category).filter(Category.slug == slug).first()

    def update(self, db, category, data):
        category.name = data["name"]
        category.slug = data["slug"]
        category.status = data["status"]

        if data.get("image"):
            # Old image delete
            if category.image:
                old_image = category.image.lstrip("/")
                if os.path.exists(old_image):
                    os.remove(old_image)

            category.image = data["image"]

        db.commit()
        db.refresh(category)

        return category

    def delete(self, db, category):
        category.deleted_at = datetime.now()
        db.commit()
        return True