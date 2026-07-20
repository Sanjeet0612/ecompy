from models.blog_category import BlogCategory
from datetime import datetime
import os


class BlogCategoryRepository:

    def create(self, db, data):
        category = BlogCategory(**data)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category


    def update(self, db, category, data):
        category.name = data["name"]
        category.slug = data["slug"]
        category.status = data["status"]

        db.commit()
        db.refresh(category)

        return category


    def delete(self):
        pass

    def bulk_delete(self):
        pass

    def get_by_id(self, db, category_id):
        return db.query(BlogCategory).filter(BlogCategory.id == category_id, BlogCategory.deleted_at == None).first()

    def get_by_name(self):
        pass

    def get_by_slug(self, db, slug):
        return db.query(BlogCategory).filter(BlogCategory.slug == slug).first()


    def get_all(self, db, page=1, limit=10, search=None, status=None):
        query = db.query(BlogCategory).filter(BlogCategory.deleted_at == None)

        # 🔍 SEARCH
        if search:
            query = query.filter(BlogCategory.name.like(f"%{search}%"))

        # 🔥 STATUS FILTER
        if status is not None and status != "":
            query = query.filter(BlogCategory.status == status)

        # TOTAL COUNT (IMPORTANT)
        total = query.count()

        # PAGINATION
        categories = query.order_by(BlogCategory.id.desc()) \
            .offset((page - 1) * limit) \
            .limit(limit) \
            .all()

        return categories, total

    def get_dropdown(self, db):

        categories = (
            db.query(BlogCategory)
            .filter(
                BlogCategory.status == 1,
                BlogCategory.deleted_at.is_(None)
            )
            .order_by(BlogCategory.name.asc())
            .all()
        )

        return [
            {
                "id": BlogCategory.id,
                "name": BlogCategory.name
            }
            for BlogCategory in categories
        ]


    def change_status(self):
        pass