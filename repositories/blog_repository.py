from models.blog_category import BlogCategory
from models.blog import Blog
from datetime import datetime
import os
from models.blog import Blog
from sqlalchemy.orm import Session
from models.blog import Blog
from schemas.blog import BlogCreate, BlogUpdate
from sqlalchemy.orm import joinedload



class BlogRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, blog_data: BlogCreate):
        blog = Blog(
            category_id=blog_data.category_id,
            title=blog_data.title,
            slug=blog_data.slug,
            short_description=blog_data.short_description,
            description=blog_data.description,
            seo_title = blog_data.seo_title,
            meta_description = blog_data.meta_description,
            meta_keywords = blog_data.meta_keywords,
            tags = blog_data.tags,
            featured_image=blog_data.featured_image,
            status=blog_data.status,
        )
        self.db.add(blog)
        self.db.flush()
        return blog

     # Update Product By Id
    
    def update(self, blog_id: int, blog_data: BlogUpdate):

        blog = (
            self.db.query(Blog)
            .filter(Blog.id == blog_id)
            .first()
        )

        if not blog:
            return None

        blog.category_id = blog_data.category_id
        blog.title = blog_data.title
        blog.slug = blog_data.slug
        blog.short_description = blog_data.short_description
        blog.description = blog_data.description
        blog.seo_title = blog_data.seo_title
        blog.meta_description = blog_data.meta_description
        blog.meta_keywords = blog_data.meta_keywords
        blog.tags = blog_data.tags
        blog.status = blog_data.status
        # Main image update karenge
        blog.featured_image = blog_data.featured_image

        #self.db.commit()
        #self.db.refresh(product)

        return blog


    def delete(self):
        pass

    def bulk_delete(self):
        pass

     # Get Blog By Id

    def get_by_id(
        self,
        blog_id: int
    ):

        try:

            blog = (
                self.db.query(Blog)
                .options(
                    joinedload(Blog.category)
                )
                .filter(
                    Blog.id == blog_id,
                    Blog.deleted_at.is_(None)
                )
                .first()
            )


            data = {
                "id": blog.id,
                "category_id": blog.category_id,
                "title": blog.title,
                "slug": blog.slug,
                "short_description": blog.short_description,
                "description": blog.description,
                "featured_image": blog.featured_image,
                "seo_title": blog.seo_title,
                "meta_description":blog.meta_description,
                "meta_keywords":blog.meta_keywords,
                "tags": blog.tags,
                "status": blog.status,
                "created_at": blog.created_at,
                "updated_at": blog.updated_at
            }

            return {
                "status": True,
                "message": "Blog fetched successfully.",
                "data": data
            }

        except Exception as e:

            return {
                "status": False,
                "message": str(e),
                "data": None
            }
        

    def get_by_slug(self):
        pass

    def get_all(self, db, page=1, limit=10, search=None, status=None):
        query = (
            db.query(Blog, BlogCategory.name.label("category_name"))
            .join(BlogCategory, Blog.category_id == BlogCategory.id)
            .filter(Blog.deleted_at == None)
        )

        # SEARCH
        if search:
            query = query.filter(Blog.name.like(f"%{search}%"))

        # STATUS FILTER
        if status is not None and status != "":
            query = query.filter(Blog.status == status)

        # TOTAL COUNT (IMPORTANT)
        total = query.count()

        # PAGINATION
        blogs = query.order_by(Blog.id.desc()) \
            .offset((page - 1) * limit) \
            .limit(limit) \
            .all()
        
        data = []

        for blog, category_name in blogs:
            data.append({
                "id": blog.id,
                "title": blog.title,
                "slug": blog.slug,
                "category_id": blog.category_id,
                "category_name": category_name,
                "featured_image": blog.featured_image,
                "created_at": blog.created_at,
                "updated_at": blog.updated_at,
                "status": blog.status
            })

        return {
            "data": data,
            "total": total
        }

    
    def change_status(self):
        pass